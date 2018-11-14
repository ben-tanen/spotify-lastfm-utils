rm(list = ls())

library(data.table)
library(tidyr)
library(ggplot2)
library(scales)

setwd('/Users/ben-tanen/Google Drive/Projects/spotify-lastfm-utils/')

# import data
# dt1 <- data.table(read.csv('data/top-artists-7days-2017-12-25-to-2018-05-07.csv'))
dt1 <- data.table(read.csv('data/top-artists-7days-30dec2017-to-28jul2018.csv'))

# set rank within date group
dt1[, rank := rank(-.SD$count, ties.method = 'last'), by = start_date]

# fill in gaps for artists with NA
dt2 <- spread(dt1[rank <= 25, -c('count', 'end_date')], key = start_date, value = rank)
dt3 <- melt(dt2, id.vars = 'name', variable.name = 'date', value.name = 'rank')

# format date
dt3$date <- as.Date(dt3$date)

# determine which bands to plot
dt3[, count := nrow(.SD[!is.na(rank)]), by = name]
dt3[, to_plot := count > length(unique(dt3$date)) * 0.7, by = name]

# plot
ggplot(dt3, aes(x = date, y = rank, group = name)) + 
    geom_hline(mapping = NULL, colour = 'grey90', size = 0.25, 
               yintercept = seq(5, max(dt3$rank, na.rm = T) - 1, 5)) +
    geom_line(data = dt3[to_plot == T], aes(color = name), size = 1.5, alpha = 0.7, na.rm = T) +
    geom_point(data = dt3[to_plot == T], aes(color = name), size = 3, alpha = 1, na.rm = T) + 
    geom_line(data = dt3[to_plot == F], size = 0.5, alpha = 0.2, color = 'gray', na.rm = T) +
    geom_point(data = dt3[to_plot == F], size = 1, alpha = 0.2, color = 'gray', na.rm = T) +
    scale_x_date(name = "Week", labels = date_format("%b %d, %Y"), expand = c(0.025, 0),
                 breaks = seq.Date(min(dt3$date), max(dt3$date), by = '7 day')) +
    scale_y_reverse(name = "Rank", limits = c(max(dt3$rank, na.rm = T), 1),
                    breaks = 1:max(dt3$rank, na.rm = T), expand = c(0.025, 0)) +
    scale_color_discrete(name = "Artist") +
    labs(title = "Artist Rank by Weekly Listens") +
    theme_light() +
    theme(plot.title = element_text(hjust = 0.5),
          plot.margin = margin(0.25, 0.25, 0.25, 0.25, 'cm'),
          axis.text.x = element_text(hjust = 0, angle = -45),
          panel.grid = element_blank())

