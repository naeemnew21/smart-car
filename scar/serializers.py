from rest_framework import serializers
from .models import Car_X, Initial
from .models import VEHICLES


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car_X
        fields = ['vehicle', 'longitude', 'latitude', 'speed', 'direction']
        
        

class InitSerializer(serializers.Serializer):
    vehicle      = serializers.CharField(max_length=8)
    longitude1   = serializers.DecimalField(max_digits=11, decimal_places=8)
    latitude1    = serializers.DecimalField(max_digits=10, decimal_places=8)
    longitude2   = serializers.DecimalField(max_digits=11, decimal_places=8)
    latitude2    = serializers.DecimalField(max_digits=10, decimal_places=8)
    
    class Meta:
        fields = ['vehicle', 'longitude1', 'latitude1', 'longitude2', 'latitude2']