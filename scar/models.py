from operator import mod
from pyexpat import model
from django.db import models



VEHICLES = [
    ('V1', 'V1'),
    ('V2', 'V3'),
    ('V3', 'V3'),
    ('V4', 'V4')
]


PATH = [
    ('1R','1R'),
    ('1L','1L'),
    ('1S','1S'),
    ('2R','2R'),
    ('2L','2L'),
    ('2S','2S'),
    ('3R','3R'),
    ('3L','3L'),
    ('3S','3S'),
    ('4R','4R'),
    ('4L','4L'),
    ('4S','4S')
]

DIRS = [('R','R'),('L','L'),('S','S')]


class Car_X(models.Model):
    vehicle     = models.CharField(max_length=8, unique=True, choices= VEHICLES)
    longitude   = models.DecimalField(max_digits=11, decimal_places=8)
    latitude    = models.DecimalField(max_digits=10, decimal_places=8)
    speed       = models.PositiveIntegerField()
    direction   = models.CharField(max_length=1 , choices=DIRS)
    time        = models.TimeField()
    
    path        = models.CharField(max_length=2 , choices=PATH)
    distance    = models.PositiveIntegerField()
    remain_time = models.TimeField()
    
    def __str__(self):
        return self.veichle
    
    
    
class Initial(models.Model):
    vehicle      = models.CharField(max_length=8, unique=True)
    intersection = models.CharField(max_length=20, default='TEST')
    init         = models.BooleanField() # if true: forward, false : go away
    
    def __str__(self):
        return self.vehicle