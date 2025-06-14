import json

from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET
from users.models import AppUser, UserSkill, Skill, SocialLink, Project, Location
from .forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .serializers import SocialLinkSerializer, ProjectSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .locations import LOCATIONS
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from azure.storage.blob import BlobServiceClient
import base64
import os
from datetime import datetime
from .azure_storage import load_azure_storage_connection_string

# Azure Storage configuration
PROFILE_PHOTOS_CONTAINER = 'profile-photos'

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, "Wrong login data!")
                form = LoginForm()
                render(request, 'users/login.html', {'form': form})
    else:
        form = LoginForm()
    is_registration = request.GET.get('registration')
    if is_registration:
        messages.success(request, "Registration success!")
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            repeated_password = form.cleaned_data.get('repeated_password')
            role = form.cleaned_data.get('role')
            position = form.cleaned_data.get('position')
            country = form.cleaned_data.get('country')
            city = form.cleaned_data.get('city')
            mobile = form.cleaned_data.get('mobile')
            starts_in = form.cleaned_data.get('starts_in')
            is_remote = form.cleaned_data.get('is_remote')
            is_hybrid = form.cleaned_data.get('is_hybrid')

            if not is_password_valid(password, repeated_password):
                form.add_error('repeated_password', 'Passwords do not match')
                return render(request, 'users/register.html', {'form': form, 'locations_json': json.dumps(LOCATIONS)})

            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already taken')
                return render(request, 'users/register.html', {'form': form, 'locations_json': json.dumps(LOCATIONS)})

            # Create Location object
            location = None
            if country and city:
                location, _ = Location.objects.get_or_create(country=country, city=city)

            create_user(first_name, last_name, email, password, role, position, location, mobile, starts_in, is_remote, is_hybrid)
            return HttpResponseRedirect('login?registration=true')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'users/register.html', {'form': form, 'locations_json': json.dumps(LOCATIONS)})
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form, 'locations_json': json.dumps(LOCATIONS)})


def create_user(first_name, last_name, email, password, role, position=None, location=None, mobile=None, starts_in=None, is_remote=False, is_hybrid=False):
    user = User.objects.create(username=email, first_name=first_name, last_name=last_name, email=email,
                               password=make_password(password))
    user.save()
    app_user = AppUser.objects.create(
        user=user,
        role=role,
        position=position,
        location=location,
        mobile=mobile,
        starts_in=starts_in,
        is_remote=is_remote,
        is_hybrid=is_hybrid
    )
    app_user.save()


def is_password_valid(password, repeated_password):
    if password != repeated_password:
        return False
    return True


def get_current_user(request):
    user = request.user
    if user:
        return HttpResponse(user)
    return HttpResponse(None)


def get_user_skills(email):
    user = AppUser.objects.filter(user=email)[0]
    user_skills = UserSkill.objects.filter(user=user)
    skills = []
    for user_skill in user_skills:
        skills.append({"name": user_skill.skill.name, "level": user_skill.level, "id": user_skill.skill.id})
    
    def level(e):
        return e['level']
    skills.sort(key=level, reverse=True)

    return skills


@require_http_methods(["POST"])
def remove_skill(request):
    email = request.user
    data = json.loads(request.body)
    id = data.get("id")
    return remove_user_skill(email, id)


def get_user_role(email):
    role = AppUser.objects.filter(user=email).first().role
    return role


def get_user(email):
    user = AppUser.objects.filter(user=email).first()
    return user


def logout_user(request):
    logout(request)


def get_current_user_data(request):
    user = get_user(request.user)
    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    user_data = {"firstName": first_name, "lastName": last_name, "email": email}
    return user_data


def remove_user_skill(email, skill_id):
    user = AppUser.objects.filter(user=email)[0]
    skill = Skill.objects.get(id=skill_id)

    if not user:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    if not skill:
        return JsonResponse({'error': 'Skill does not exist'}, status=404)

    user_skill = UserSkill.objects.filter(user=user, skill=skill)[0]
    if not user_skill:
        return JsonResponse({'error': 'No such skill for the user'}, status=404)

    user_skill.delete()

    return JsonResponse({'message': 'Skill deleted successfully'}, status=201)


@api_view(['POST'])
def add_social_link(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    app_user = get_user(request.user)
    if not app_user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SocialLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=app_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_social_links(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    app_user = get_user(request.user)
    if not app_user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    social_links = SocialLink.objects.filter(user=app_user)
    serializer = SocialLinkSerializer(social_links, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_social_link(request, link_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        social_link = SocialLink.objects.get(id=link_id, user__user=request.user)
        social_link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SocialLink.DoesNotExist:
        return Response({'error': 'Social link not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_social_link(request, link_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        social_link = SocialLink.objects.get(id=link_id, user__user=request.user)
        serializer = SocialLinkSerializer(social_link, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except SocialLink.DoesNotExist:
        return Response({'error': 'Social link not found'}, status=status.HTTP_404_NOT_FOUND)


@login_required
@require_http_methods(["POST"])
def update_position(request):
    try:
        data = json.loads(request.body)
        position = data.get('position')
        
        if not position:
            return JsonResponse({'error': 'Position is required'}, status=400)
            
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        user.position = position
        user.save()
        
        return JsonResponse({'message': 'Position updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_location(request):
    try:
        data = json.loads(request.body)
        country = data.get('country')
        city = data.get('city')
        is_remote = data.get('is_remote', False)
        is_hybrid = data.get('is_hybrid', False)
        
        if not country or not city:
            return JsonResponse({'error': 'Country and city are required'}, status=400)
            
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        # Get or create Location object
        location, _ = Location.objects.get_or_create(country=country, city=city)
        
        user.location = location
        user.is_remote = is_remote
        user.is_hybrid = is_hybrid
        user.save()
        
        return JsonResponse({'message': 'Location updated successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def add_project(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    app_user = get_user(request.user)
    if not app_user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=app_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
@require_http_methods(["POST"])
def delete_project(request, project_id):
    try:
        user = get_user(request.user)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        try:
            project = user.projects.get(id=project_id)
            project.delete()
            return JsonResponse({'message': 'Project deleted successfully'}, status=200)
        except user.projects.model.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_project(request, project_id):
    try:
        data = json.loads(request.body)
        project = get_object_or_404(Project, id=project_id, user=get_user(request.user))
        
        if 'title' in data:
            project.title = data['title']
        if 'description' in data:
            project.description = data['description']
        if 'technologies' in data:
            project.set_technologies(data['technologies'])
        if 'githubLink' in data:
            project.github_link = data['githubLink']
        if 'demoLink' in data:
            project.demo_link = data['demoLink']
        if 'order' in data:
            project.order = data['order']
            
        project.save()
        
        return JsonResponse({
            'message': 'Project updated successfully',
            'project': {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'technologies': project.get_technologies(),
                'githubLink': project.github_link,
                'demoLink': project.demo_link,
                'order': project.order
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def remove_profile_photo(request):
    # TODO: Implement photo removal
    return JsonResponse({"success": True})


@login_required
def add_profile_photo(request):
    if request.method == "POST":
        try:
            # Get the base64 image data from the request
            image_data = request.POST.get('image')
            if not image_data:
                return JsonResponse({"success": False, "error": "No image data provided"})

            # Remove the data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]

            # Decode the base64 data
            image_bytes = base64.b64decode(image_data)

            # Generate a unique filename
            filename = f"{request.user.id}.jpg"

            # Get connection string and initialize the BlobServiceClient
            connection_string = load_azure_storage_connection_string()
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(PROFILE_PHOTOS_CONTAINER)

            # Upload the blob
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(image_bytes, overwrite=True)

            # Get the blob URL
            blob_url = blob_client.url

            # Update user's profile photo URL in the database
            request.user.profile_photo = blob_url
            request.user.save()

            return JsonResponse({
                "success": True,
                "photo_url": blob_url
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


def get_profile_photo(user_id):
    """
    Tries to retrieve the profile photo for the given user ID from Azure Blob Storage.
    Returns the image bytes if found, otherwise returns False.
    """
    try:
        filename = f"{user_id}.jpg"
        connection_string = load_azure_storage_connection_string()
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(PROFILE_PHOTOS_CONTAINER)
        blob_client = container_client.get_blob_client(filename)
        stream = blob_client.download_blob()
        image_bytes = stream.readall()
        return image_bytes
    except Exception:
        return False
