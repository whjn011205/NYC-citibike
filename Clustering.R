## Pre Section: Import library
library("mclust")

##############################################################
##################### data preparation #######################
##############################################################
trip_col <- read.csv("2013.csv")
names(trip_col)
trip_col <- trip_col[-which(trip_col$grid_x==-1|trip_col$grid_y==-1),]
trip_col$grid <- trip_col$grid <- paste(trip_col$grid_x,trip_col$grid_y)
trip_col <- trip_col[,-c(1,2,3,4)]

############################################################
###################### k-means Clustering ##################
############################################################

kValue <- 2:100
percentageVar <- rep(0,99)
result <- data.frame(kValue=kValue,percentageVar=percentageVar)

for(i in kValue){
  set.seed(333)
  km <- kmeans(x=trip_col[,-ncol(trip_col)], centers = i, iter.max = 30, nstart = 50)
  result[result$kValue==i,"percentageVar"] <- km$betweenss/km$totss
}

plot(result$kValue,result$percentageVar,type="b",xlab="k",ylab="percentage of variance")
points(7,result$percentageVar[7],col="red",cex=2)

set.seed(333)
km <- kmeans(x=trip_col[,-ncol(trip_col)], centers = 7, iter.max = 30, nstart = 50)
print(km$cluster)

## print the cluster member
for(i in 1:7){
  data <- trip_col[which(km$cluster==i),]
  write.csv(data,file=paste("data",i,".csv",sep=""))
}

#################################################
#################### GMM ########################
#################################################

mc <- Mclust(data=trip_col[,-ncol(trip_col)], G=7)
summary(mc)

## print the cluster member
for(i in 1:7){
  data <- trip_col[which(mc$classification==i),]
  write.csv(data,file=paste("data",i,".csv",sep=""))
}

# comparison with true clusters and K-means

table(km$cluster, mc$classification)

##############################################################
##################### hierarchical clustering ################
##############################################################
d <- dist(trip_col[,-ncol(trip_col)], method = "euclidean")
# try different linkages
hc.c <- hclust(d)  # default method="complete"
hc.a <- hclust(d, method="average") 
hc.s <- hclust(d, method="single") 

hc.c.clusters <- cutree(hc.c, 7) # specify the number of cluster eventually
hc.c.clusters

## print the cluster member
for(i in 1:7){
  data <- trip_col[which(hc.c.clusters==i),]
  write.csv(data,file=paste("data",i,".csv",sep=""))
}

## comparison with true clusters and K-means
table(km$cluster, hc.c.clusters)

plot(hc.c,labels=FALSE)
abline(h=115, lty=2, col="red")
