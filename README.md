### Introduction
This project is written for [Insight Data Engineering Coding Challenge](https://github.com/InsightDataScience/donation-analytics).

### How to run
`python ./src/donation-analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt`
or
`./run.sh`

### Algorithm
The following is a quick summary of the algorithm:

1. For each line in itcont.txt
2. Parse the line and extracts useful information. If the information is malformed, skip and ignore the line (back to step 1)
3. Identify if the donor is a repeated donor by checking if the donor's name and zip code is in `repeat_donors_dict`. If not, create a new mapping in `repeat_donors_dict` with `(name, zip_code)` as key, and the year of contribution as value, and continue to the next line in itcont.txt (back to step 1)
4. Check if year of contribution is from a previous calender year. If yes, skip and ignore the record (back to step 1)
5. Update the total amount of contributions and total number of transactions received by recipient from the contributor's zip code streamed in so far in this calendar year from repeat donors in a `repeat_donations_dict`. 
6. Compute the n-th percentile value
7. Write the information about contributions received by recipient from the contributor's zip code streamed in so far in this calendar year from repeat donors to repeat_donor.txt

### Design Decisions
To compute the n-th percentile value, I used two heaps (`max_heap` and `min_heap`) to optimize the computation. This allows the time complexity of finding the n-th percentile value to be `O(log(n))`, instead of `O(nlog(n))` if a list is used since the list needs to be sorted. The ordinal rank of the n-th percentile value is computed using the nearest-rank method, and is the size of `max_heap`. Thus `max_heap` contains the smallest n% of all contributions, i.e. the largest value of the `max_heap` is the n-th percentile value, and `min_heap` contains the rest of the elements. If the new transaction amount is less than the largest value in `max_heap`, add the new amount into `max_heap`; otherwise, add the new amount to `min_heap`. Then, if the size of `max_heap` is larger than the ordinal rank of the n-th percentile value (meaning `max_heap` contains more than n% of contributions), the largest value of `max_heap` is moved to `min_heap`. Similar if the size of `max_heap` is smaller than the ordinal rank of the n-th percentile value. Since Python's heapq only supports min heap, max heap is implemented by using the negative of the value.

When creating `repeat_donor_dict` to keep track of contributions from repeated donors, I decided to store the total amount of contributions and the total number of transactions, instead of computing those two values at each iteration. The reason for that is to decrease time complexity. We can avoid computing the sum of all contributions and number of transactions, which would be `O(n)`, instead of `O(1)` by storing and updating those two values at each iteration, while only increasing the size of the value of the dictionary by two integers. 
