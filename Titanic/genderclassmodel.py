import csv as csv 
import numpy as np

csv_file_object = csv.reader(open('data/train.csv', 'rb')) 
header = csv_file_object.next()
data=[]

for row in csv_file_object:
    data.append(row)
data = np.array(data)

#Determine number of fare brackets.
fare_ceiling = 40
data[ data[0::,9].astype(np.float) >= fare_ceiling, 9 ] = fare_ceiling - 1.0
fare_bracket_size = 10
number_of_price_brackets = fare_ceiling / fare_bracket_size

#Determine number of classes by finding the number of unique entries in the class row.
number_of_classes = len(np.unique(data[0::,2])) 

#Initialize the survival table with all zeros
survival_table = np.zeros((2, number_of_classes, number_of_price_brackets))

#Find proportion of survivors.
for i in xrange(number_of_classes):
    for j in xrange(number_of_price_brackets):

        women_only_stats = data[ (data[0::,4] == "female") \
                                 & (data[0::,2].astype(np.float) == i+1) \
                                 & (data[0:,9].astype(np.float) >= j*fare_bracket_size) \
                                 & (data[0:,9].astype(np.float) < (j+1)*fare_bracket_size), 1]

        men_only_stats = data[ (data[0::,4] != "female") \
                                 & (data[0::,2].astype(np.float) == i+1) \
                                 & (data[0:,9].astype(np.float) >= j*fare_bracket_size) \
                                 & (data[0:,9].astype(np.float) < (j+1)*fare_bracket_size), 1]

        survival_table[0,i,j] = np.mean(women_only_stats.astype(np.float))  # Female stats
        survival_table[1,i,j] = np.mean(men_only_stats.astype(np.float))    # Male stats

#Convert nan to 0
survival_table[ survival_table != survival_table ] = 0.

#Print survival_table will proportions of survivors.
print survival_table

#If proportion of survivors is greater than or equal to .5, 1 for survived. If less, 0.
survival_table[ survival_table < 0.5 ] = 0
survival_table[ survival_table >= 0.5 ] = 1

#Reprint survival_table.
print survival_table

test_file = open('data/test.csv', 'rb')
test_file_object = csv.reader(test_file)
header = test_file_object.next()
predictions_file = open("data/genderclassmodel.csv", "wb")
p = csv.writer(predictions_file)
p.writerow(["PassengerId", "Survived"])

for row in test_file_object:
	for j in xrange(number_of_price_brackets):
		try:
			row[8] = float(row[8])
		except:
			bin_fare = 3 - float(row[1])
			break
		if row[8] > fare_ceiling:
			bin_fare = number_of_price_brackets-1
			break
		if row[8] >= j * fare_bracket_size\
			and row[8] < (j+1) * fare_bracket_size:
			bin_fare = j
			break
	if row[3] == 'female':p.writerow([row[0], "%d" % int(survival_table[0, float(row[1])-1, bin_fare])])
	else: p.writerow([row[0], "%d" % int(survival_table[1, float(row[1])-1, bin_fare])])

test_file.close() 
predictions_file.close()