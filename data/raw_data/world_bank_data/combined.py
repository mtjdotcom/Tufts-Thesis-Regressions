combine = open("combine_3.csv","a")

for line in open("page1.csv"):
	combine.write(line)

for num in range(2,15):
	f = open("page"+(str(num)+".csv"))
	for line in f:
		combine.write(line)
	f.close()

combine.close()

