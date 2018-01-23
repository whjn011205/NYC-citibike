#############################################
############## prepare data #################
#############################################
col_time <- read.csv("col_time_new.csv")

names(col_time)
dim(col_time)

names(col_time) <- c("grid_x","grid_y","month","yr","target_time","accident_count","n_inj","n_kill","age","trip_count","duration","citigrid","cluster")
names(col_time)
head(col_time)

for(i in 1:9){
  addition <- toString(i);
  month <- paste("0",addition,sep="")
  col_time[which(col_time$month==i),"month"] <- month
}

col_time$grid <- paste(col_time$grid_x,col_time$grid_y)
col_time$yr_month <- paste(col_time$yr,col_time$month,sep="")

# delete the grid without complete data
ag <- aggregate(x = col_time[,c(10,11)], by=list(grid=col_time$grid), length)
names(ag) <- c("grid","grid_count","yr_month")
noCompleteGrid <- ag[which(ag$grid_count!=4),"grid"]
for(i in 1:length(noCompleteGrid)){
  if(any(col_time$grid==noCompleteGrid[i])){
    col_time <- col_time[-which(col_time$grid==noCompleteGrid[i]),]
  }
}

gridNA <- col_time[which(is.na(col_time$target_time)),"grid"]
if(length(gridNA)!=0){
  for(i in 1:length(gridNA)){
    if(any(col_time$grid==gridNA[i])){
      col_time <- col_time[-which(col_time$grid==gridNA[i]),]
    }
  }
}

monthNa <- col_time[which(is.na(col_time$month)),"grid"]
if(length(monthNa!=0)){
  for(i in 1:length(monthNa)){
    if(any(col_time$grid==monthNa[i])){
      col_time <- col_time[-which(col_time$grid==monthNa[i]),]
    }
  }
}

#############################################
###### Difference in Difference  ############
#############################################

#############################################
###### only consider one cluster ############
#############################################

partial_col_time <- col_time[which(col_time$cluster==2),]

## TIME: whether the time is excessed the time 201307 or not
partial_col_time$time <- ifelse(partial_col_time$yr_month >= 201307, 1, 0)

## TREATED: this grid contains citibike or not
partial_col_time$treated <- ifelse(partial_col_time$citigrid == 1, 1, 0)
partial_col_time$treated[is.na(partial_col_time$treated)] <- 0

didreg <- lm(target_time ~ treated * time + accident_count + n_inj, data = partial_col_time)
summary(didreg)

#didreg_alt <- lm(accident_ccount ~ treated * time, data = partial_col_time)
#summary(didreg_alt)

#############################################
############### T test ######################
#############################################
# Calculate change percentage in target_time
changePercentage <- function(x){
  percentage <- (as.numeric(x[4]) - as.numeric(x[1]))/as.numeric(x[1])
  return(percentage)
}
ag_version2 <- aggregate(x = col_time[,c(5,10)], by=list(grid=col_time$grid), changePercentage)
ag_version2 <- ag_version2[,-ncol(ag_version2)]

treatedGrid <- unique(partial_col_time[which(partial_col_time$citigrid==1),"grid"])
controlGrid <- unique(partial_col_time[which(is.na(partial_col_time$citigrid)),"grid"])

for(i in 1:length(treatedGrid)){
  if(i == 1)
    treated <- ag_version2[which(ag_version2$grid==treatedGrid[i]),]
  else
    treated <- rbind(treated,ag_version2[which(ag_version2$grid==treatedGrid[i]),])
}

for(i in 1:length(controlGrid)){
  if(i == 1)
    control <- ag_version2[which(ag_version2$grid==controlGrid[i]),]
  else
    control <- rbind(control,ag_version2[which(ag_version2$grid==controlGrid[i]),])
}

t.test(x=treated[,-1], y=control[,-1], alternative="less",conf.level = 0.9)

#############################################
########## Weight T test ####################
#############################################
library(weights)

xResidual <- didreg$residuals[which(partial_col_time$citigrid==1)]
yResidual <- didreg$residuals[which(is.na(partial_col_time$citigrid))]

calculateWeight <- function(grid,residual){
  j <- 1
  weight <- rep(NA,length(grid))
  for(i in seq(from=1,to=length(residual),by=4)){
    weight[j] <- 1/(residual[i]+residual[i+1]+residual[i+2]+residual[i+3])^2
    j <- j + 1
  }
  return(weight)
}

if(length(xResidual)!=0 & length(yResidual)!=0){
  xWeight <- calculateWeight(treatedGrid,xResidual)
  yWeight <- calculateWeight(controlGrid,yResidual)

  print("cluster 3")
  wtd.t.test(x=treated[,-1], y=control[,-1], 
             weight=xWeight, weighty=yWeight,alternative="less")
}

