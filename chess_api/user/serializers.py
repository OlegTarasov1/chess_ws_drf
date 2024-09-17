from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only = True)
    games_played = serializers.IntegerField(read_only = True)
    games_won = serializers.IntegerField(read_only = True)
    games_lost = serializers.IntegerField(read_only = True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'score', 'games_played', 'games_won', 'games_lost']


class UserRegistrationSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only = True)
    games_played = serializers.IntegerField(read_only = True)
    games_won = serializers.IntegerField(read_only = True)
    games_lost = serializers.IntegerField(read_only = True)
    password = serializers.CharField(write_only = True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model()(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    class Meta:
        model = get_user_model()
        fields = '__all__'