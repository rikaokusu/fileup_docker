from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from rest_framework import serializers
from .serializers import *
from django.utils import timezone
from . import models
from .models import Address, Group


class GetUpdateModalSerializer(ModelSerializer):

    class Meta:
        model = Address
        fields = [
            'id',
            'legal_or_individual',
            'legal_personality',
            'legal_person_posi',
            'company_name',
            'trade_name',
            'department_name',
            'last_name',
            'first_name',
            'email',
            'full_name_preview'
        ]


class GetGroupUpdateModalSerializer(ModelSerializer):

    class Meta:
        model = Group
        fields = [
            'id',
            'group_name',
            'address',

        ]
