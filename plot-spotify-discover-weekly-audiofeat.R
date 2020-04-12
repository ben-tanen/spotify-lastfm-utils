library(data.table)
library(dplyr)
library(ggplot2)
library(patchwork)

# set directory
setwd('/Users/ben-tanen/Google Drive/Projects/spotify-lastfm-utils/')

# import data
dt <- data.table(read.csv('data/saved-vs-discoverweekly-audiofeat-25Mar2020.csv'))

# make plots
plots <- list()
for (var in c("acousticness", "danceability", "energy", "instrumentalness", 
              "key", "liveness", "loudness", "mode", "speechiness", "tempo", "valence")) {
  print(var)
  plots[[var]] <- ggplot(dt, aes_string(x = "source", y = var)) + geom_boxplot()
}

# stitch together plots with patchwork
multiplot <- function(plots, n_col = 3, n_row = NULL) {
    is.null(n_row)
}

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  print(numPlots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

multiplot(plotlist = objects(pattern = "p_"))
