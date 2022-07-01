from math import sqrt
from django.shortcuts import get_object_or_404, render
from .models import VEHICLES, Car_X, Initial, Inter
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from .serializers import CarSerializer, InitSerializer, ResponseSerializer, InterSerializer
import geopy.distance
import numpy
import math
from datetime import datetime, timedelta


'''
                  *
              ==========|===========
              |         |          |
              |    1    |    2     |  *
              |         |          |
              ----------|-----------
              |         |          |
          *   |    3    |    4     |
              |         |          |
              ==========|===========
                              *

'''


PATH_X = {
    '1R':['1R','1L','1S','2S','2L','4L'],
    '1L':['1R','1L','1S','3R','3L','3S','4R','4L','4S','2S','2L'],
    '1S':['1R','1L','1S','3R','3L','3S','2S','2L','4L'],
    
    '2R':['2R','2L','2S','4S','4L','3L'],
    '2L':['2R','2L','2S','3R','3L','3S','1R','1L','1S','4S','4L'],
    '2S':['2R','2L','2S','1R','1L','1S','4S','4L','3L'],
    
    '3R':['3R','3L','3S','1S','1L','2L'],
    '3L':['3R','3L','3S','4R','4L','4S','2R','2L','2S','1S','1L'],
    '3S':['3R','3L','3S','4R','4L','4S','1S','1L','2L'],
    
    '4R':['4R','4L','4S','3S','3L','1L'],
    '4L':['4R','4L','4S','2R','2L','2S','1R','1L','1S','3S','3L'],
    '4S':['4R','4L','4S','2R','2L','2S','3S','3L','1L']
}


#initialize intersection
NAME     = 'TEST'
try:
    obj = Inter.objects.get(name = 'TEST')
    REF      = (obj.latc, obj.longc) #center of intersection (lat, long)
    POSITION = [(obj.lat1,obj.long1),(obj.lat2,obj.long2),(obj.lat3,obj.long3),(obj.lat4,obj.long4)] # 1,2,3,4 of intesection
except:
    REF      = (45, 90) #center of intersection (lat, long)
    POSITION = [(46,89),(46,91),(44,89),(44,91)] # 1,2,3,4 of intesection


def initialized(vehicle, x = NAME):
    obj   = Initial.objects.filter(vehicle=vehicle, intersection=x)
    exist = obj.exists()
    if exist:
        return obj[0].init
    return False



def get_distance(coords_1, coords_2): # (lat, long)
    distance = geopy.distance.distance(coords_1, coords_2).m
    return round(distance, 3)


def get_direction(point1, point2, ref = REF):
    d1   = get_distance(point1, ref)
    d2   = get_distance(point2, ref)
    diff = d1 - d2
    if diff > 0:
        return 'A' # forward --> to interesction
    elif diff < 0:
        return 'B' # go away from intersection
    return 'C' # static


def get_path(point, direction, x = POSITION): # direction : Right, Left or Straight
    d1 = get_distance(point, x[0])
    d2 = get_distance(point, x[1])
    d3 = get_distance(point, x[2])
    d4 = get_distance(point, x[3])
    listOfElems = [d1, d2, d3, d4]
    if len(listOfElems) != len(set(listOfElems)):
        return False, 0
    m = min(listOfElems)
    if d1 == m:
        return '1{}'.format(direction), 0
    elif d2 == m:
        return '2{}'.format(direction), 1
    elif d3 == m:
        return '3{}'.format(direction), 2
    elif d4 == m:
        return '4{}'.format(direction), 3
    


def get_remain(speed, distance):
    # speed in m/s, distance in m
    return distance//speed # return remain time in seconds
    



def get_bearing(lat1, long1, lat2, long2):
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    brng = numpy.arctan2(x,y)
    brng = numpy.degrees(brng)
    if brng < 0:
        brng += 360
    return brng



def get_stop_point(coord, distance, ref): # distance : in meters
    bearing = get_bearing(*ref, *coord)
    return geopy.distance.distance(meters=distance).destination(ref, bearing=bearing)



def extract_data(V, point, direction, speed):
    path, ref     = get_path(point, direction)
    if not(path):
        return False
    distance      = get_distance(point, POSITION[ref]) # REF is position of intersection
    remain        = get_remain(speed, distance)
    time_expected = datetime.now() + timedelta(seconds= remain)
    Car_X.objects.update_or_create(vehicle = V, defaults={
                                                        'latitude' : point[0],
                                                        'longitude' : point[1],
                                                        'speed' : speed,
                                                        'direction' : direction,
                                                        'time' : datetime.now(),
                                                        'path' : path,
                                                        'distance' : distance,
                                                        'remain_time': remain,
                                                        'expected_time' :time_expected
                                                                     } )
    return True



class Initialize_Intersection(UpdateAPIView):
    queryset = Inter.objects.all()
    serializer_class   = InterSerializer
    lookup_field = 'name'
    
    def get_object(self):
        obj   = Inter.objects.filter(name = 'TEST')
        exist = obj.exists()
        if not(exist):
            Inter.objects.create(name='TEST')
            obj   = Inter.objects.filter(name = 'TEST')
        return obj[0]
      
    def perform_update(self, serializer):
        serializer.save()     
        global   REF, POSITION 
        obj      = Inter.objects.get(name = 'TEST')
        REF      = (obj.latc, obj.longc) #center of intersection (lat, long)
        POSITION = [(obj.lat1,obj.long1),(obj.lat2,obj.long2),(obj.lat3,obj.long3),(obj.lat4,obj.long4)] # 1,2,3,4 of intesection

           
           
           
class Initialize_Car(GenericAPIView):
    serializer_class   = InitSerializer
    
    def post(self, request, *args, **kwargs):
           serializer = self.get_serializer(request.data)
           vehicle = serializer.data['vehicle']
           point1  = (float(serializer.data['latitude1']), float(serializer.data['longitude1']))
           point2  = (float(serializer.data['latitude2']), float(serializer.data['longitude2']))
           decision = get_direction(point1, point2)
           if decision == 'A':
               Initial.objects.update_or_create(vehicle = vehicle, defaults={'init' : True} )
               return Response({'status':'forward'})
           elif decision == 'B':
               Initial.objects.update_or_create(vehicle = vehicle, defaults={'init' : False} )
               return Response({'status':'go away'})
           else:
               return Response({'status':'fail'})
           




class GetAction(GenericAPIView):
    serializer_class   = CarSerializer
    
    
    def post(self, request, *args, **kwargs):
       serializer = self.get_serializer(request.data)
       vehicle    = serializer.data['vehicle']
       if not(initialized(vehicle)) :
           return Response({'status':'fail-not initialized'})
       
       point     = (float(serializer.data['latitude']), float(serializer.data['longitude']))
       direction = serializer.data['direction']
       speed     = serializer.data['speed']
       
       
       data = extract_data(vehicle, point, direction, speed)
       if data:
            response = ResponseSerializer(Car_X.objects.get(vehicle=vehicle))
            return Response(response.data)
       return Response({'status':'fail-data error'})
    