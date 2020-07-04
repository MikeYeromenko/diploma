from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from API_admin import serializers as serial
from seance.models import SeatCategory, Price, Film, Hall, SeanceBase, Seance


class ViewSetInsertMixin:
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    def perform_update(self, serializer):
        serializer.save(admin=self.request.user)


class SeatCategoryViewSet(ViewSetInsertMixin, viewsets.ModelViewSet):
    queryset = SeatCategory.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.SeatCategoryHyperSerializer
        else:
            return serial.SeatCategoryCUDSerializer


class PriceViewSet(viewsets.ModelViewSet):
    serializer_class = serial.PriceHyperSerializer
    queryset = Price.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.PriceHyperSerializer
        else:
            return serial.PriceCUDSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.seance.is_active:
            return Response({'detail': f'Can\'t delete, it relates to active seance'}, status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FilmViewSetMixin(ViewSetInsertMixin, viewsets.ModelViewSet):
    queryset = Film.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.FilmHyperSerializer
        else:
            return serial.FilmCUDSerializer


class HallViewSetMixin(ViewSetInsertMixin, viewsets.ModelViewSet):
    serializer_class = serial.HallHyperSerializer
    queryset = Hall.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.HallHyperSerializer
        else:
            return serial.HallCUDSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.base_seances.count():
            return Response(f'There are related to this hall '
                            f'SeanceBase objects. Can\'t delete', status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateSeatsAPIView(CreateAPIView):
    permission_classes = (IsAdminUser, )
    serializer_class = serial.SeatModelSerializer

    def post(self, request, *args, **kwargs):
        serializer = serial.CreateSeatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        hall = get_object_or_404(Hall, pk=kwargs.get('pk'))
        seat_category = get_object_or_404(SeatCategory, pk=serializer['seat_category'].value)
        hall.create_or_update_seats(seat_category=seat_category,
                                    row=serializer['row'].value,
                                    number_starts=serializer['seat_starts'].value,
                                    number_ends=serializer['seat_ends'].value)
        result = hall.activate_hall()
        if result['success']:
            return Response({
                'created_seats': serial.SeatModelSerializer(hall.seats.all(), many=True).data,
                'detail': f'Hall is successfully activated'
            }, status=status.HTTP_200_OK)
        return Response({
                'created_seats': serial.SeatModelSerializer(hall.seats.all(), many=True).data,
                'detail': f'There leaved {result["uncreated_seats"]} uncreated seats'
            }, status=status.HTTP_201_CREATED)


class SeanceBaseViewSet(viewsets.ModelViewSet):
    queryset = SeanceBase.objects.all()
    permission_classes = (IsAdminUser, )

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.SeanceBaseHyperSerializer
        else:
            return serial.SeanceBaseCUDSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.seances.count():
            return Response({'detail': f'Can\'t delete. '
                                       f'There are related seances to this s_base'}, status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SeanceViewSetMixin(ViewSetInsertMixin, viewsets.ModelViewSet):
    queryset = Seance.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serial.SeanceHyperSerializer
        else:
            return serial.SeanceCUDSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.tickets.all().count() or instance.prices.all().count():
            return Response({'detail': f'Can\'t delete. '
                                       f'There are related objects to this seance'}, status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SeanceActivateView(UpdateAPIView):
    queryset = Seance.objects.all()
    serializer_class = serial.SeanceHyperSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        result = instance.activate()
        if result['success']:
            return Response(f'Seance was successfully activated.', status=status.HTTP_200_OK)
        return Response({'errors': result['errors_list'],
                         'seat_categories_with_no_price:':
                             serial.SeatCategoryHyperSerializer(result['seat_categories'], many=True,
                                                                context={'request': request}).data
                         }, status=status.HTTP_200_OK)


class SeanceByParamsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serial.SeanceHyperSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        queryset = Seance.objects.all()
        hall_pk = self.request.GET.get('hall_pk')
        starts = self.request.GET.get('starts')
        ends = self.request.GET.get('ends')
        if hall_pk:
            hall = get_object_or_404(Hall, pk=hall_pk)
            queryset = queryset.filter(seance_base__hall=hall)
        if starts:
            queryset = queryset.filter(time_starts__gt=starts)
        if ends:
            queryset = queryset.filter(time_starts__lt=ends)
        return queryset
