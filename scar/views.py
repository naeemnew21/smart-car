from math import sqrt
from django.shortcuts import render
from .models import VEHICLES, Car_X, Initial
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import CarSerializer, InitSerializer


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
REF      = (90, 45) #center of intersection
POSITION = [(89,46),(91,46),(89,44),(91,44)]



def initialized(vehicle, x = NAME):
    exist = Initial.objects.filter(vehicle=vehicle, intersection=x).exists()
    if exist:
        return exist.init
    return False



def get_distance(start, end): # stop : point 1,2,3 or 4 of intersection
    distance = sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
    return round(distance, 3)


def get_direction(point1, point2, ref = REF):
    d1   = get_distance(point1, ref)
    d2   = get_distance(point2, ref)
    diff = d1 - d2
    if diff > 0:
        return 'A'
    elif diff < 0:
        return 'B'
    return 'C'


def get_path(point, direction, x = POSITION): # direction : Right, Left or Straight
    d1 = get_distance(point, x[0])
    d2 = get_distance(point, x[1])
    d3 = get_distance(point, x[2])
    d4 = get_distance(point, x[3])
    listOfElems = [d1, d2, d3, d4]
    if len(listOfElems) == len(set(listOfElems)):
        return False
    m = min(listOfElems)
    if d1 == m:
        return '1{}'.format(direction)
    elif d2 == m:
        return '2{}'.format(direction)
    elif d3 == m:
        return '3{}'.format(direction)
    elif d4 == m:
        return '4{}'.format(direction)
    


def get_remain(speed, distance):
    # speed in m/s, distance in m
    return distance//speed
    



class Initialize_car(GenericAPIView):
    serializer_class   = InitSerializer
    
    def post(self, request, *args, **kwargs):
           serializer = self.get_serializer(request.data)
           vehicle = serializer.data['vehicle']
           point1  = (float(serializer.data['longitude1']), float(serializer.data['latitude1']))
           point2  = (float(serializer.data['longitude2']), float(serializer.data['latitude2']))
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
       
       if not(initialized(serializer.data['vehicle'])) :
           return Response({'status':'fail'})
       
       point     = (float(serializer.data['longitude']), float(serializer.data['latitude']))
       direction = serializer.data['direction']
       speed     = serializer.data['speed']
       
       path = get_path(point, direction)
       distance = get_distance(point, REF) # REF is position of intersection
       time = get_remain(speed, distance)
       
       data = {'path':path, 'distancce':distance, 'time':time}
       
       return Response(data)
    