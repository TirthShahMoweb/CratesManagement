from rest_framework import serializers

from ..models import User



class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile_number',)

    def validate(self, attrs):
        if not User.objects.filter(mobile_number = attrs.get('mobile_number')).exists():
            raise serializers.ValidationError("No user found with this details.")
        return attrs