from mrjob.job import MRJob
from mrjob.step import MRStep
import mrjob.compat
import os
import math
import json

class MRNearestNeighbor(MRJob):

    # Override steps to perform two rounds of map-reduce:
    def steps(self):
        return [
            MRStep(mapper=self.mapper_r1,
                   reducer=self.reducer_r1),
            MRStep(mapper=self.mapper_r2,
                   reducer=self.reducer_r2)
        ]

    def configure_args(self):
        # For dimension arguments:
        super(MRNearestNeighbor, self).configure_args()
        self.add_file_arg('--query')
        
    
    def mapper_r1(self, _, line):
        # Generate key-value pairs:

        # Parse encoding line:
        in_elements = line.strip().split(" ")
        img_path = in_elements[0]
        vector_elements = [float(x.replace(',', '').
                                   replace('[', '').
                                   replace('"', '').
                                   replace(']','')) for x in in_elements[1:]]

        # Hash encoding into one of 20 groups:
        group = int((sum(vector_elements[0:100]) * 19823) % 20)

        # Yield key as group and the name/encoding as value.
        yield (group, (img_path, vector_elements))

    def reducer_r1(self, key, values):

    	# Parse query encoding (uploaded in command line call).
        with open('./vec.txt') as f:
            for line in f:
                out = line.split(" ")

        # Convert query encoding to 
        query = [float(x) for x in out]

        # Loop through encodings in value list and calculate Euclidean distance:
        for vector in values:

            if len(vector[1]) == 0:
                continue

            dist = [float((float(a) - float(b))**2) for a, b in zip(query, vector[1])]
            dist = math.sqrt(sum(dist))

            yield (1, (dist, vector[0]))

    def mapper_r2(self, key, values):
        # Identity:
        yield key, values

    def reducer_r2(self, key, values):
        
        # Sort by distance:
        vals = [x for x in values]
        sorted_vals = sorted(vals, key= lambda x: x[0])

        # Return top 20 results:
        yield key, sorted_vals[0:20] 

# Driver:
if __name__ == '__main__':
    MRNearestNeighbor.run()