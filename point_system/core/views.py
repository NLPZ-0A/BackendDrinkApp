import re
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, QRCode,Item, RedeemedItem
from .serializers import UserSerializer, QRCodeSerializer, ItemSerializer, RedeemedItemerializer
from django.db import transaction
import random
import string

@api_view(['POST'])
def register_qr(request):
    print("post")
    print(request)
    
    
    qr_code = request.data.get('qr_code')
    user_phone = request.data.get('phone_number')
    number_process = re.findall(r'\d+', user_phone)  # Extrae solo los números
    phone_number = ''.join(number_process)
    
    print(qr_code, user_phone, phone_number)

    # Buscar al usuario y al código QR en la base de datos
    try:
        user = User.objects.get(phone_number=phone_number)
        qr = QRCode.objects.get(code=qr_code, used_by__isnull=True)
    except (User.DoesNotExist, QRCode.DoesNotExist) as error:
        print(error)
        return Response({'error': 'Código QR inválido o ya utilizado'}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar si es el primer canje del usuario
    is_first_combo = not QRCode.objects.filter(used_by=user).exists()

    # Asignar puntos y marcar el QR como usado
    with transaction.atomic():
        # Asignar puntos al usuario actual
        user.points += qr.points
        user.save()

        # Marcar el QR como usado
        qr.used_by = user
        qr.save()

        message_gift = ''

        print(qr.gift)
        if(len(str(qr.gift)) > 0 and qr.gift != None ):
            message_gift =  f'Felicidades ganaste {qr.gift} de premio!!!'

        print(f'referido del user {user.referred_by}')

        message = ''
        # Verificar si el usuario fue referido por otro usuario
        if user.referred_by:
            referrer = user.referred_by

            message_refer = f'Haz ganado 20 puntos gracias a +{user_phone}'
            # Otorgar puntos al referidor solo si es el primer canje
            referral_points = 100 if is_first_combo else 20

            if referral_points > 0:
                referrer.points += referral_points
                referrer.save()

                # Enviar notificación al referidor usando WhatsApp
                message = f"Has ganado {qr.points} puntos por tu compra Y tu referente {referrer.name} ha ganado {referral_points} puntos."

                message_refer =f'Has ganado { referral_points } puntos por la compra del combo de uno de tus referidos'

                if referral_points >= 100:
                    message_refer =f'Has ganado { referral_points } puntos por la compra del primer combo de uno de tus referidos'

                # send_whatsapp_notification(referrer.phone_number, message)
                print(f"Notificación enviada a {referrer.phone_number}: {message}")
            
            # Responder con los puntos ganados tanto por el QR como por el referido
            return Response({
                'message': message,
                'message_gift' : message_gift,
                'referrer_number': referrer.phone_number,
                'message_refer': message_refer,
            }, status=status.HTTP_200_OK)
        
        # Si no hay referido, solo se devuelven los puntos del QR
        return Response({
            'message': f'¡Felicidades! Has ganado {qr.points} puntos.',
            'message_gift' : message_gift,
            
            }, status=status.HTTP_200_OK) 
    
@api_view(['POST'])
def refer_system(request):
    print("post")
    print(request)

    user_phone = request.data.get('phone_number')
    referrer_phone_number = request.data.get('refer')

    number_process = re.findall(r'\d+', user_phone)  # Extrae solo los números
    phone_number = ''.join(number_process) 

    print(phone_number)
    print(referrer_phone_number)

    if not phone_number or not referrer_phone_number:
        return Response({'error': 'Ha ocurrido un error, intente colocar los datos correctamente o ponte en contacto con nosotros.'}, status=status.HTTP_400_BAD_REQUEST)

    print(phone_number)
    # Verificar si el usuario ya existe
    existing_user = User.objects.filter(phone_number=phone_number).first()

    if not existing_user:
        return Response({'error': 'Tu usuario aún no se ha creado, genera tu usuario primero desde el /menu.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener el usuario que refiere usando el código de referido
    referrer = User.objects.filter(referral_code=referrer_phone_number).first()
    if not referrer:
        return Response({'error': 'El usuario del referido aún no existe.'}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar si el referidor ya ha alcanzado el límite de referidos
    referrer_counts = referrer.referidos.all()


    print(referrer_counts)
    if len(referrer_counts) >= 5:
        return Response(
            {'error': '*Este usuario ya ha llegado al límite de los 5 referidos, intenta con otro usuario.*‼️'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificar si ya ha sido referido anteriormente
    if existing_user.referred_by is not None:
        return Response(
            {'error': '*Este usuario ya ha sido referido anteriormente.*⭕'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    print(f' referr {referrer}')
    print(f'existing {existing_user.referred_by}')
    # Verificar si se está intentando crear una relación cíclica (evitar que el referido refiera al que lo refirió)
    if existing_user == referrer.referred_by:
        return Response(
            {'error': '*No puedes referir a un usuario que ya te ha referido a ti.* ⭕:p'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if referrer == existing_user:
        return Response(
            {'error': '*No puedes referirte a ti mismo!*❌)'},
            status=status.HTTP_400_BAD_REQUEST
        )

    print(f" existing user {existing_user}")
    # Asignar el referenciador al usuario
    existing_user.referred_by = referrer
    existing_user.save()

    #referrer.points += 100 (solo si es la primera compra o evento)
    referrer.save()

    return JsonResponse({
        'message': '*Referente asignado con éxito!*☑️',
        'from_number': phone_number,
        'referrer': referrer.phone_number
    })


@api_view(['GET'])
def get_referrals(request, phone_number ):
    #user_phone = request.query_params.get('phone_number')
    try:
        print(f'consulta referidos de {phone_number}')
    
        number_process = re.findall(r'\d+', phone_number)  # Extrae solo los números
        phone_number = ''.join(number_process)
        print(phone_number)
        # Verificar si el usuario existe
        user = User.objects.filter(phone_number=phone_number).first()
        print(user)
        if not user:
            print('el usuario no existe')
            return Response({'error': 'El usuario no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener todos los referidos de este usuario
        referrals = user.referidos.all()
        print(referrals)
        # Devolver la lista de números de teléfono de los referidos
        referral_numbers = [referral.phone_number for referral in referrals]

        if len(referral_numbers) <= 0:
            print('no tienes ningun referido')
            return Response({'error': 'No tienes ningun referido aún.'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(referral_numbers)
        
        return Response({
            'referral_numbers': referral_numbers,
            'total_referrals': len(referral_numbers)
        }, status=status.HTTP_200_OK)
    except Exception as error:
        print(f'error => {error}')

        return Response({
            'error': error
            
        }, status=status.HTTP_404_NOT_FOUND)


#----------------------------------------------OBTENER MIS OBJETOS-----------------------------------------------------------------
@api_view(['GET'])
def get_redeemed_items(request, phone_number):
    #user = get_object_or_404(User, phone_number=phone_number)
    user = User.objects.filter(phone_number=phone_number).first()

    if not user:
        return Response({'error': 'El usuario no existe, cree uno en el menu de opciones.'}, status=status.HTTP_400_BAD_REQUEST)
    
    redeemed_items = user.redeemed_items.all()
    
    items_list = [
        {   'id': redeemed_item.item.id,
            'item_name': redeemed_item.item.name,
            'quantity': redeemed_item.quantity,
            'redeemed_at': redeemed_item.redeemed_at
        }
        for redeemed_item in redeemed_items
    ]

    if not items_list:
        return Response({'message': '*Aún no has canjeado ningún objeto.*❌🎒'}, status=status.HTTP_200_OK)
    
    return Response({
        'redeemed_items': items_list,
    }, status=status.HTTP_200_OK)

#-----------------------------------------LOGICA DE INTERCAMBIO DE OBJETOS-------------------------------------
@api_view(['POST'])
def redeem_item(request):
    try:
        user_phone = request.data.get('phone_number')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        user = get_object_or_404(User, phone_number=user_phone)
        item = get_object_or_404(Item, id=item_id)

        total_points_required = item.points_required * quantity

        if user.points < total_points_required:
            return Response({
                'error': 'No tienes suficientes puntos para canjear este objeto.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if item.available_units < quantity:
            return Response({
                'error': 'No hay suficientes unidades disponibles para este objeto.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Realizar el canje dentro de una transacción atómica
        with transaction.atomic():
            # Descontar puntos del usuario
            user.points -= total_points_required
            user.save()

            # Reducir las unidades disponibles del objeto
            item.available_units -= quantity
            item.save()

            # Registrar el canje del objeto
            redeemed_item = RedeemedItem.objects.create(
                user=user,
                item=item,
                quantity=quantity
            )

        # Serializar el objeto Item
        item_serializer = ItemSerializer(item)

        return Response({
            'item': item_serializer.data,
            'message': f'¡Has canjeado {quantity} {item.name}(s)!',
            'remaining_points': user.points
        }, status=status.HTTP_200_OK)
    
    except Exception as error:
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)


#--------------------------------------CONSULTAR OBJETOS DISPONIBLES---------------------------------------------------------
@api_view(['GET'])
def get_available_items(request):
    items = Item.objects.filter(available_units__gt=0)

    items_list = [
        {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'points_required': item.points_required,
            'available_units': item.available_units
        }
        for item in items
    ]

    return Response({
        'available_items': items_list,
    }, status=status.HTTP_200_OK)



#-------------------------------------------------------CHECK POINTS-------------------------------------------------------
@api_view(['GET'])
def check_points(request, phone_number):
    try:
        print(f'{phone_number}  consulto sus puntos ')
        user = User.objects.get(phone_number=phone_number)
        print(user)
        print(user.points)
        return Response({'points': user.points}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        error = 'Lea atentamente: *su usuario no ha sido encontrado, si no ha registrado su numero, hagalo con el comando registrar:"minombre" sin las comillas.*🟢'
        return Response({'error': error }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def check_code(request, phone_number):
    try:
        user = User.objects.get(phone_number=phone_number)
        return Response({'code': user.referral_code}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': '*Usuario no encontrado*🔴'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_referral_code(request):
    user_phone = request.data.get('phone_number')

    try:
        user = User.objects.get(phone_number=user_phone)
        if not user.referral_code:
            user.referral_code = generate_referral_code()
            user.save()
        return Response({'referral_code': user.referral_code}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_profile(request):

    try:
        user_phone = request.data.get('phone_number')
        number_process = re.findall(r'\d+', user_phone)  # Extrae solo los números
        phone_number = ''.join(number_process) 
        referral_code = generate_code()

        name = request.data.get('name')

        # Validar que el número de teléfono y nombre no estén vacíos
        if not user_phone or not name:
            return Response({'error': '*Faltan datos: nombre o número de teléfono*❌.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el usuario ya existe
        if User.objects.filter(phone_number=phone_number ).exists():
            return Response({'error': '*Tu número de teléfono ya está registrado*❌'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el usuario
        user = User.objects.create(phone_number=phone_number, name=name, referral_code=referral_code)
        
        return Response({'message': f'*Perfil creado para {name} con el número +{phone_number}*☑️'}, status=status.HTTP_201_CREATED)
    except Exception as error:
        print(error)
        return Response({'message': '*ha ocurrido un error en el proceso*❌'}, status=status.HTTP_400_BAD_REQUEST)


def generate_code():
    caracteres = string.ascii_letters + string.digits  # Letras mayúsculas, minúsculas y dígitos
    codigo = ''.join(random.choices(caracteres, k=8))
    return codigo

def generate_referral_code():
    # Generar un código único aquí (por ejemplo, usando random o algún hash)
    return 'REF123'
