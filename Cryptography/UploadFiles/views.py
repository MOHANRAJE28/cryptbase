from django.shortcuts import render
from .forms import MyFileForm
from .models import MyFileUpload
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from cryptography.fernet import Fernet
import os 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
#login code
from django.http import HttpResponse
from cryptography.fernet import Fernet
from .models import MyFileUpload
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
            else:
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid username or password.'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = SignUpForm()
    return render(request, 'login.html', {'form': form})


# home

def home(request):
    mydata=MyFileUpload.objects.all()
    myform=MyFileForm()
    if mydata !='':
        context={'form':myform,'mydata':mydata}
        return render(request,"index.html",context)
    else:
        context={'form':myform}
        return render(request,"index.html",context)
 
def decrypt(request):
    mydata=MyFileUpload.objects.all()
    myform=MyFileForm()
    if mydata !='':
        context={'form':myform,'mydata':mydata}
        return render(request,"decrypt.html",context)
    else:
        context={'form':myform}
        return render(request,"decrypt.html",context)


import cv2
import os
import numpy as np

# upload image
import cv2
import numpy as np
import tempfile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseServerError
from .models import MyFileUpload
from io import BytesIO

def uploadfile(request):
    if request.method == "POST":
        myform = MyFileForm(request.POST, request.FILES)
        if myform.is_valid():
            MyFileName = request.FILES['file'].name
            MyFileFormat = MyFileName.split('.')[-1]

            # Read the uploaded image using OpenCV
            uploaded_image = request.FILES['file'].read()
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file.write(uploaded_image)
            tmp_file.close()

            # Encrypt the image
            try:
                image_input = cv2.imread(tmp_file.name, 0)
                (x1, y) = image_input.shape
                image_input = image_input.astype(float) / 255.0
                mu, sigma = 0, 0.1  
                key = np.random.normal(mu, sigma, (x1, y)) + np.finfo(float).eps
                image_encrypted = image_input / key
            except Exception as e:
                return HttpResponseServerError(f"Error encrypting the image: {e}")

            # Save the encrypted image to a temporary file with .png extension
            encrypted_tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            cv2.imwrite(encrypted_tmp_file.name, image_encrypted * 255)

            # Read the encrypted image from the temporary file
            encrypted_image = encrypted_tmp_file.read()
            encrypted_tmp_file.close()

            # Save the encrypted image data to the database
            try:
                my_file_upload = MyFileUpload(file_name=MyFileName, file_format=MyFileFormat)
                my_file_upload.my_file.save(MyFileName, InMemoryUploadedFile(BytesIO(encrypted_image), None, MyFileName, 'image/png', len(encrypted_image), None))
                my_file_upload.save()
            except Exception as e:
                return HttpResponseServerError(f"Error saving the encrypted image to the database: {e}")

            messages.success(request, "Image uploaded and encrypted successfully")
            return redirect("home")

    return redirect("home")


# def uploadfile(request):
#     global image_encrypted
#     if request.method == "POST":
#         myform = MyFileForm(request.POST, request.FILES)
#         if myform.is_valid():
#             MyFileName = request.FILES['file'].name
#             MyFileFormat = MyFileName.split('.')[-1]
    
              # Key = "Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
              # f = Fernet(Key)
              # encrypted_data = f.encrypt(request.FILES['file'].read())
#             # Create an InMemoryUploadedFile instance with encrypted data
#             encrypted_file = InMemoryUploadedFile(BytesIO(image_encrypted), 'file', MyFileName, 'image/jpeg', len(image_encrypted), None)
#             # Save the encrypted image data to the database
#             MyFileUpload.objects.create(file_name=MyFileName, my_file=encrypted_file, file_format=MyFileFormat)
            
#             messages.success(request, "Image uploaded and encrypted successfully")
#             return redirect("home")

#     return redirect("home")

          


# def uploadfile(request):
#     if request.method == "POST":
#         myform = MyFileForm(request.POST, request.FILES)
#         if myform.is_valid():
#             MyFileName = request.FILES['file'].name
#             MyFileFormat = MyFileName.split('.')[-1]
#             Key = "Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
#             f = Fernet(Key)
#             encrypted = f.encrypt(request.FILES['file'].read())
#             from django.core.files.uploadedfile import InMemoryUploadedFile
#             from io import BytesIO
#             MyFile = InMemoryUploadedFile(BytesIO(encrypted), 'file', MyFileName, 'application/octet-stream', len(encrypted), None)
#             MyFileUpload.objects.create(file_name=MyFileName, my_file=MyFile, file_format=MyFileFormat)
#             messages.success(request, "File uploaded successfully")
#             return redirect("home")

#     return redirect("home")



def download_file(request, file_id):
    try:
        encrypted_file = MyFileUpload.objects.get(pk=file_id)
        Key = "Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
        f = Fernet(Key)
        decrypted_data = f.decrypt(encrypted_file.my_file)
        content_type = 'application/octet-stream'
        response = HttpResponse(decrypted_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{encrypted_file.file_name}"'  
        return response
    except MyFileUpload.DoesNotExist:
        return HttpResponse("File not found", status=404)
    
import os
from django.contrib import messages
from django.shortcuts import redirect
from .models import MyFileUpload

def deleteFile(request, id):
    try:
        mydata = MyFileUpload.objects.get(id=id)
        file_path = mydata.my_file.path
        mydata.delete()
        os.remove(file_path)
        messages.success(request, 'File deleted successfully')
    except MyFileUpload.DoesNotExist:
        messages.error(request, 'File not found')
    except Exception as e:
        messages.error(request, f'An error occurred: {e}')
    return redirect('home')

# def deleteFile(request,id):
#     mydata=MyFileUpload.objects.get(id=id)
#     mydata.delete()
#     os.remove(mydata.my_file.path)
#     messages.success(request,'File Deleted successfully')
#     return redirect('Home')



# def uploadfile(request):
#     if request.method=="POST":
#         myform=MyFileForm(request.POST,request.FILES)
#         if myform.is_valid():
#             MyFileName = request.POST.get('file_name')
#             MyFile = request.FILES.get('file')
#             # Change this to your secret key
#             # with  open('myKey.Key','rb') as myKey:
#             Key="Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
#             f=Fernet(Key)
#             #encrypt
#             encrypted = f.encrypt(MyFile.read())
#             MyFile=MyFile.write(encrypted)
#             MyFileUpload.objects.create(file_name=MyFileName,my_file=MyFile).save()
#             messages.success(request,"File uploaded successfully")
#         return redirect("home")

# def uploadfile(request):
#     if request.method=="POST":
#         myform=MyFileForm(request.POST,request.FILES)
#         if myform.is_valid():
#             MyFileName = request.POST.get('file_name')
#             MyFile = request.FILES.get('file')
#             MyFileFormat= MyFile.content_type
#             # Change this to your secret key
#             Key="Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
#             f=Fernet(Key)
#             #encrypt
#             encrypted = f.encrypt(MyFile.read())
#             # Create a new InMemoryUploadedFile with the encrypted data
#             from django.core.files.uploadedfile import InMemoryUploadedFile
#             from io import BytesIO
#             # MyFile = InMemoryUploadedFile(BytesIO(encrypted), 'file', MyFileName, MyFileFormat, len(encrypted), None)
#             MyFile = InMemoryUploadedFile(BytesIO(encrypted), 'file', MyFileName, 'application/octet-stream', len(encrypted), None)
#             MyFileUpload.objects.create(file_name=MyFileName, my_file=MyFile,file_format=MyFileFormat).save()
#             messages.success(request,"File uploaded successfully")
#         return redirect("home")   
    #  file_format=MyFileFormat
# def downloadfile(request, file_id):
#     # Fetch the file from the database
#     my_file_upload = MyFileUpload.objects.get(id=file_id)
#     MyFile = my_file_upload.my_file
#     # Read the encrypted data
#     encrypted = MyFile.read()
#     # Change this to your secret key
#     Key="Azxn8wddQnM7sbPSlkF1pmULaCp8oFJfb1NygwNcqss="
#     f=Fernet(Key)
#     # Decrypt
#     decrypted = f.decrypt(encrypted)
#     # Create a new InMemoryUploadedFile with the decrypted data
#     from django.core.files.uploadedfile import InMemoryUploadedFile
#     from io import BytesIO
#     MyFile = InMemoryUploadedFile(BytesIO(decrypted), 'file', my_file_upload.file_name, 'application/octet-stream', len(decrypted), None)
#     # Now you can send the file to the user
#     response = FileResponse(MyFile, as_attachment=True, filename=my_file_upload.file_name)
#     return response
