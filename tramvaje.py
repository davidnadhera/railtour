from datetime import datetime,time,timedelta

with open("C:\\idos\\odjezdy-tram.txt", "a+") as file1:
    with open("C:\\idos\\prijezdy-tram.txt", "a+") as file2:
    # Writing data to a file
        curr_time = datetime(day=10, month=8, year=2022, hour=23,minute=35)
        curr_cislo = 4490001
        while curr_time < datetime(day=11, month=8, year=2022, hour=3,minute=36):
            file1.write(f"2916,tr,{curr_cislo},{curr_time.strftime('%H:%M')}\n")
            time2 = curr_time + timedelta(minutes=17)
            file2.write(f"2914,tr,{curr_cislo},{time2.strftime('%H:%M')}\n") 
            # file1.write(f"2915,tr,{curr_cislo},{time2.strftime('%H:%M')}\n")
            # time3 = curr_time + timedelta(minutes=25)
            # file2.write(f"2912,tr,{curr_cislo},{time3.strftime('%H:%M')}\n") 
            curr_time = curr_time + timedelta(minutes=15)
            curr_cislo = curr_cislo + 2