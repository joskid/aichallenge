#!/usr/bin/env python
from map import *
from random import randint
from collections import defaultdict

class HeightMapMap(Map):
    def __init__(self, options={}):
        super(HeightMapMap, self).__init__(options)
        self.name = 'height_map'
        self.rows = options.get('rows', (40,120))
        self.cols = options.get('cols', (40,120))
        self.players = options.get('players', (2,4))
        self.land = options.get('land', (85, 90))
    
    def generate(self):
        # pick random full size for map
        rows = self.get_random_option(self.rows)        
        cols = self.get_random_option(self.cols)
        
        # ensure map rows:cols ratio is within 2:1
        while cols < rows // 2 or cols > rows * 2:
            cols = self.get_random_option(self.cols)
            
        # calc max players that can be tiled
        row_max = rows//16
        col_max = cols//16
        player_max = row_max*col_max
        
        players = self.get_random_option(self.players)
        # ensure player count choosen is within max
        while players > player_max:
            players = self.get_random_option(self.players)
            
        # pick random grid size
        # ensure grid rows < row_max
        # ensure grid cols < col_max
        divs = [(i, players//i)
                for i in range(1,min(players+1, row_max+1))
                if players % i == 0        
                    and players//i < col_max]
        if len(divs) == 0:
            # there were no acceptable grid sizes for map
            # usually do to a prime number of players which has to be 1xN
            return self.generate()
        row_sym, col_sym = choice(divs)
        
        # fix dimensions for even tiling
        rows //= row_sym
        cols //= col_sym            
        
        # get percent of map that should be land
        land = self.get_random_option(self.land)        

        # initialize height map
        height_map = [[0]*cols for _ in range(rows)]
    
        # cut and lift
        iterations = 500
        for _ in range(iterations):
            row = randint(0, rows-1)
            col = randint(0, cols-1)
            radius = randint(5, (rows+cols)/4)
            radius2 = radius**2
            for d_row in range(-radius, radius+1):
                for d_col in range(-radius, radius+1):
                    h_row = (row + d_row) % rows
                    h_col = (col + d_col) % cols
                    if self.euclidean_distance2((row, col), (h_row, h_col), (rows, cols)) <= radius2:
                        height_map[h_row][h_col] += 1
        
        # create histogram
        histo = defaultdict(int)
        for height_row in height_map:
            for height in height_row:
                histo[height] += 1
    
        # find sea and snow levels
        map_area = rows * cols
        sea_level = min(histo.keys())
        snow_level = max(histo.keys())
        max_water = map_area * (100 - land) // 100
        sea_area = histo[sea_level]
        snow_area = histo[snow_level]
        while sea_area + snow_area < max_water:
            sea_level += 1
            sea_area += histo[sea_level]
            if sea_area + snow_area >= max_water:
                break
            snow_level -= 1
            snow_area += histo[snow_level]

        # initialize map
        self.map = [[LAND]*cols for _ in range(rows)]
                
        # place salty and frozen water
        for row in range(rows):
            for col in range(cols):
                if (height_map[row][col] <= sea_level
                        or height_map[row][col] >= snow_level):
                    self.map[row][col] = WATER
        #self.toText()
        self.fill_small_areas()
        
        # check too make sure too much wasn't filled in, only 2 percent of area
        areas = self.section(0)
        water_area = map_area - len(areas[0][0])
        added_area = water_area - snow_area - sea_area
        if map_area * 2 // 100 < added_area:
            return self.generate()
        
        # place player start in largest unblockable section
        areas = self.section()
        row, col = choice(areas[0][0])
        self.map[row][col] = ANTS
        # center ant in section
        d_row = rows//2 - row
        d_col = cols//2 - col
        self.translate((d_row, d_col))

        # finish map        
        self.tile((row_sym, col_sym))
        self.make_wider()
        
def main():
    new_map = HeightMapMap()
    new_map.generate()
    
    # check that all land area is accessable
    while new_map.allowable() != None:
        print(new_map.allowable())
        new_map.generate()
        
    new_map.toText()
    
if __name__ == '__main__':
    main()