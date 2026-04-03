from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
import json
from django.http import JsonResponse
from django.contrib import messages
from.forms import RegisterUserForm
from.forms import UserUpdateForm
from.forms import ProfileUpdateForm
from.forms import UpdateIDForm
from.forms import AddLetter
from.forms import DeptandDesignationForm
from.forms import AddIDForm
from.forms import AddDivision
from.forms import AddDivisionForm
from.forms import LetterAction
from.forms import LetterActionARDO
from.forms import LetterActionARDA
from.forms import LetterActionRD
from.forms import ProfilePicture
from.forms import LetterActionmsgcenter

#from datetime import datetime, timedelta
from datetime import timedelta#for message center
from django.utils import timezone#for message center

from.forms import AddDivision1
from django.contrib.auth.forms import UserCreationForm
from .models import Employee
from.models import ID
from .models import Forclaim
from .models import Idcode
from .models import DeptandDesignation
from .models import Idapplication
from .models import AddID
from .models import ForclaimAdmin
from .models import Letter
from .models import DivisionOffice
from .models import AddDivisionww
from .models import SampleLetter, SampleNotification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random #IDCODE generate
import string #capwords

from tablib import Dataset
from .resources import ForclaimResource
from .resources import ForclaimResourceAdmin
from .resourcesdept import DeptandDesignationResource


from django.shortcuts import get_object_or_404
import csv
from django.http import FileResponse
from io import BytesIO
#import operator
import os

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from itertools import chain

#for pdf generation

from xhtml2pdf import pisa
from django.template.loader import get_template






from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import messaging
from django.contrib.auth.models import User
from .models import FCMToken
from .utils import *  # Ensure Firebase is initialized
from django.db.models import Q
from mega import Mega #for mega
import tempfile



def routingslip_pdf(request,*args, **kwargs):
   
    pk =kwargs.get('pk')
    routingslip = get_object_or_404(Letter, pk=pk)
    
    user = User.objects.get(username=routingslip.user)
    rank = AddDivisionww.objects.get(user=user.id)
    
   
    template_path ='routingslip_pdf.html'
    context = {'routingslip':routingslip,'user':user,'rank':rank}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']= 'filename="routing_slip.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>'+ html + '</pre>')
    return response







@csrf_exempt
def register_token(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.POST.get('username'))
        token = request.POST.get('token')
        
        # Save the token in the database
        FCMToken.objects.update_or_create(user=user, defaults={'token': token})
        
        return JsonResponse({'message': 'Token registered successfully'})
    return HttpResponse("Only POST method is allowed.")

@csrf_exempt
def send_notification(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.POST.get('username'))
        token_obj = FCMToken.objects.get(user=user)
        
        message = messaging.Message(
            notification=messaging.Notification(
                title='Test Notification',
                body='This is a test notification.',
            ),
            token=token_obj.token,
        )
        
        response = messaging.send(message)
        return JsonResponse({'message': 'Notification sent successfully', 'response': response})
    return HttpResponse("Only POST method is allowed.")







def test(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_broadcast",
        {
            'type':'send_notification',
            'message': "Notification"

        }
    )
    return HttpResponse("DOne")


@login_required(login_url='loginuser')
def updateletter(request, id):
    letter = get_object_or_404(Letter, id=id)

    if request.method == "POST":
        form = AddLetter(request.POST, request.FILES, instance=letter)

        if form.is_valid():
            reg = form.save(commit=False)
            reg.action_request = request.POST.get('actionrequest', '')

            uploaded_file = request.FILES.get('letter_pdf_file')

            # Initialize Mega
            mega = Mega()
            m = mega.login(os.environ.get('MEGA_EMAIL'), os.environ.get('MEGA_PASSWORD'))

            if uploaded_file:
                # 🔴 DELETE OLD FILE
                if reg.mega_file_id:
                    try:
                        files = m.get_files()
                        print("Stored Mega ID:", reg.mega_file_id)

                        if reg.mega_file_id in files:
                            m.delete(reg.mega_file_id)
                            print("Old file deleted successfully")
                        else:
                            print("Old file not found:", reg.mega_file_id)
                    except Exception as e:
                        print("Delete error:", e)

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                # Find or create "Letter" folder
                files = m.get_files()
                folder_id = None
                for key, value in files.items():
                    if value['t'] == 1 and value['a']['n'] == 'Letter':
                        folder_id = key
                        break
                if not folder_id:
                    folder = m.create_folder('Letter')
                    folder_id = list(folder.values())[0]

                # Upload new file
                uploaded = m.upload(tmp_path, folder_id, uploaded_file.name)

                # ✅ Extract real Mega file ID
                file_id = uploaded['f'][0]['h']

                reg.mega_file_id = file_id
                reg.letter_pdf = m.get_upload_link(uploaded)

                os.remove(tmp_path)

            # Update text fields
            reg.letter_desc = form.cleaned_data['letter_desc'].upper()
            reg.sender = form.cleaned_data['sender'].upper()

            reg.save()
            messages.success(request, "Letter updated successfully!")
            return redirect('displayletter')

    else:
        form = AddLetter(instance=letter)

    return render(request, 'updateletter.html', {'form': form})



'''
@login_required(login_url='loginuser')
def updateletter(request, id):
    letter = get_object_or_404(Letter, id=id)

    if request.method == "POST":
        form = AddLetter(request.POST, request.FILES, instance=letter)

        if form.is_valid():
            reg = form.save(commit=False)

            # Handle checkbox
            action_request = request.POST.get('actionrequest', '')
            reg.action_request = action_request

            uploaded_file = request.FILES.get('letter_pdf_file')

            from mega import Mega
            import tempfile
            import os

            mega = Mega()
            m = mega.login(
                os.environ.get('MEGA_EMAIL'),
                os.environ.get('MEGA_PASSWORD')
            )

            # =========================
            # ONLY DELETE OLD FILE IF NEW FILE IS UPLOADED
            # =========================
            if uploaded_file:
                if reg.mega_file_id:
                    try:
                        m.delete(reg.mega_file_id)
                    except Exception as e:
                        print("Failed to delete old file:", e)

                # Save new file
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                # Find or create folder
                folders = m.get_files()
                folder_id = None

                for key, value in folders.items():
                    if value['t'] == 1 and value['a']['n'] == 'Letter':
                        folder_id = key
                        break

                if not folder_id:
                    folder_id = m.create_folder('Letter')

                # Upload new file
                uploaded = m.upload(tmp_path, folder_id, uploaded_file.name)

                # Update fields
                reg.letter_pdf = m.get_upload_link(uploaded)
                reg.mega_file_id = uploaded

                os.remove(tmp_path)

            # =========================
            # TEXT UPDATES
            # =========================
            reg.letter_desc = form.cleaned_data['letter_desc'].upper()
            reg.sender = form.cleaned_data['sender'].upper()

            reg.save()

            messages.success(request, "Letter updated successfully!")
            return redirect('displayletter')

    else:
        form = AddLetter(instance=letter)

    return render(request, 'updateletter.html', {'form': form})'''


'''
@login_required(login_url='loginuser')
def updateletter(request,id):
    submitted = False
    if request.method == 'POST':

        if not Letter.objects.filter(id=id):
            profile = AddDivisionww()
            profile.user_id = request.user.id
            
            u_form = UserUpdateForm(request.POST,instance=request.user)
            #p_form = AddDivision1(request.POST,request.FILES, instance=profile)
            p_form = AddDivisionForm(request.POST,instance=profile)
            p_form.user_id=request.user.id

            print(p_form.user_id)
            if p_form.is_valid() and u_form.is_valid():
                p_form.save()
                u_form.save()
                messages.success(request,f'Your Account has been Updated11111')
                return redirect('index')
            print('diri')

        else:
            letter = Letter.objects.get(id=id)
            u_form = AddLetter(request.POST,request.FILES,instance=letter)
            #fish = AddDivisionww.objects.get(user_id=request.user)  
            #p_form = AddDivisionForm(request.POST,instance=fish)
     
    
            if u_form.is_valid():
                u_form.save()
                messages.success(request,f'Letter Update Succesfully')
                return redirect('displayletter')
           
    else:
        
        if not Letter.objects.filter(id=id):
            u_form = AddLetter(instance=id)

            #p_form = AddDivisionForm(instance=request.user)
          
        else:
            letter = Letter.objects.get(id=id)       
            
            u_form = AddLetter(instance=letter)

            #fish = AddDivisionww.objects.get(user_id=request.user)       
            #p_form = AddDivisionForm(instance=fish)
         
            
            
    context= {
        'u_form':u_form,
        #'p_form':p_form,
    }

    return render(request,'updateletter.html',context)'''








"""def displaypdf(request,id):
    #filepath = os.path.join('media/pdf/letters', '14.pdf')
    pdf = Letter.objects.filter(id=id)
    #dispatch = Letter.objects.get(id=id)
    #dispatch.dispatch = "Dispatched"
    #dispatch.save()
    for item in pdf:
        aa=str(item.letter_pdf)
        id='media/'+aa
    print(aa)
    filepath = os.path.join(id)
    cleaned_filename = filepath.replace('_', ' ')
    #print(cleaned_filename)
    #print(filepath)
    return FileResponse(open(filepath,'rb'), content_type='application/pdf')"""
'''
def displaypdf(request, id):
    pdf = Letter.objects.filter(id=id)

    for item in pdf:
        file_rel_path = str(item.letter_pdf)  # example: 'pdf/letters/example_file.pdf'
        file_full_path = os.path.join('media', file_rel_path)

        # Get original filename and remove underscores (optional)
        original_filename = os.path.basename(file_full_path)
        cleaned_filename = original_filename.replace('_', ' ')

        # Open in browser (inline)
        response = FileResponse(open(file_full_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{cleaned_filename}"'
        return response

    return HttpResponseNotFound('File not found')'''
def displaypdf(request, id):
    letter = get_object_or_404(Letter, id=id)

    if letter.letter_pdf:
        return redirect(letter.letter_pdf)

    return HttpResponseNotFound('File not found')

def displaypdfmsgcenter(request, id):
    letter = get_object_or_404(Letter, id=id)
    letter.dispatch = "Dispatched"
    letter.save()
    return redirect(letter.letter_pdf)



'''
def displaypdfmsgcenter(request,id):
    #filepath = os.path.join('media/pdf/letters', '14.pdf')
    pdf = Letter.objects.filter(id=id)
    dispatch = Letter.objects.get(id=id)
    dispatch.dispatch = "Dispatched"
    dispatch.save()
    for item in pdf:
        aa=str(item.letter_pdf)
        id='media/'+aa
    print(aa)
    filepath = os.path.join(id)
    return FileResponse(open(filepath,'rb'), content_type='application/pdf')'''


    #return FileResponse(open(filepath, 'rb'), content_type='application/msword')




def searchletter(request):
    if request.method == "POST":
        searched = request.POST['searched']
        h=string.capwords(searched)
        f=searched.upper()
       
        idapplication = Letter.objects.filter(letter_desc__contains=f)or Letter.objects.filter(sender__contains=f)or Letter.objects.filter(date_send__contains=f)or Letter.objects.filter(aprover_1__contains=f)or Letter.objects.filter(bjmptrans_no__contains=f)
          
        context={
            'idapplication':idapplication
        }
        return render(request,'searchletter.html',context)
    else:
        return render(request,'searchletter.html',{})



def notificationread(request,id,id2):
    if request.method == "POST":

        """searched = request.POST['searched']
        h=string.capwords(searched)
        f=searched.upper()"""
        print("passs")

    else:
        notification = SampleNotification.objects.get(id=id2)
        notification.is_read = True
        notification.save()
        
        idapplication = Letter.objects.filter(bjmptrans_no=id)
        
        context={
            'idapplication':idapplication
        }
        return render(request,'searchletter.html',context)
        """return render(request,'searchletter.html',{})"""



def searchletterarda(request):
    if request.method == "POST":
        searched = request.POST['searched']
        h=string.capwords(searched)
        f=searched.upper()
        print(f)
       
        idapplication = Letter.objects.filter(letter_desc__contains=f)or Letter.objects.filter(sender__contains=f)or Letter.objects.filter(date_send__contains=f)or Letter.objects.filter(aprover_2__contains=f)or Letter.objects.filter(bjmptrans_no__contains=f)
          
        context={
            'idapplication':idapplication
        }
        return render(request,'searchletterarda.html',context)
    else:
        return render(request,'searchletterarda.html',{})

def searchletterrd(request):
    if request.method == "POST":
        searched = request.POST['searched']
        h=string.capwords(searched)
        f=searched.upper()
        print(f)
       
        idapplication = Letter.objects.filter(letter_desc__contains=f)or Letter.objects.filter(sender__contains=f)or Letter.objects.filter(date_send__contains=f)or Letter.objects.filter(aprover_2__contains=f)or Letter.objects.filter(bjmptrans_no__contains=f)
          
        context={
            'idapplication':idapplication
        }
        return render(request,'searchletterrd.html',context)
    else:
        return render(request,'searchletterrd.html',{})

@login_required(login_url='loginuser')
def displaymsgcenter(request):
    now = timezone.now()

    seven_day_before = now - timedelta(days=7)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    user = AddDivisionww.objects.filter(user=request.user)
    for item in user:
        if item.division_name=='MESSAGE_CENTER':
            orders4 = Letter.objects.filter(Q(stat_3='Approved', date_send__gte=seven_day_before) |Q(stat_3__in=['On Leave', 'Official Business'])).order_by('-dispatch', 'user', '-date_send')
            #orders4=Letter.objects.filter(stat_3='Approved')and Letter.objects.filter(Q(stat_3='Approved')|Q(stat_3='On Leave')|Q(stat_3='Official Business')).order_by('-dispatch','user','-date_send',)
            
            #for item3 in orders4:
            context ={'orders':orders4}
            return render(request,"displaymsgcenter.html",context)
        else:
                return redirect('addletter')



@login_required(login_url='loginuser')
def displayletterRCDS(request):
    user = AddDivisionww.objects.filter(user=request.user)

    # Iterate over all users
    for item in user:
        # Create a base filter for the letters
        orders1 = Letter.objects.filter(
            Q(aprover_1=item.division_name) |
            Q(aprover_2=item.division_name) |
            Q(aprover_3=item.division_name) |
            Q(aprover_4=item.division_name) |
            Q(sender=item.division_name)
        )
        
        # Iterate over the filtered letters
        for item1 in orders1:
            if item1.aprover_3 == item.division_name and item1.stat_2 != "Pending":  # RD
                orders4 = Letter.objects.filter(
                    aprover_3=item.division_name
                ).filter(
                    Q(stat_1='Approved') |
                    Q(stat_2='Approved') |
                    Q(stat_2='On Leave') |
                    Q(stat_2='Official Business')
                ).exclude(
                    Q(stat_3='Approved') |
                    Q(stat_1='Disapproved') |
                    Q(stat_4='Disapproved') |
                    Q(stat_2='Disapproved') |
                    Q(stat_2='Pending')
                ).order_by('-stat_3', '-updated_date')

                context = {'orders': orders4}
                return render(request, "display_letter1111.html", context)

            elif item1.aprover_2 == item.division_name and item1.stat_4 != "Pending":  # ARDA
                orders2 = Letter.objects.filter(
                    aprover_2=item.division_name
                ).filter(
                    Q(stat_4='Approved') |
                    Q(stat_4='On Leave') |
                    Q(stat_4='Official Business')
                ).exclude(
                    Q(stat_2='Approved') |
                    Q(stat_2='Disapproved') |
                    Q(stat_2='On Leave') |
                    Q(stat_2='Official Business') |
                    Q(stat_4='Pending')
                ).order_by('-stat_2', '-updated_date')

                context = {'orders': orders2}
                return render(request, "display_letter111.html", context)

            elif item1.aprover_4 == item.division_name and item1.stat_1 != "Pending":  # ARDO
                orders2 = Letter.objects.filter(
                    aprover_4=item.division_name
                ).filter(
                    Q(stat_1='Approved') |
                    Q(stat_1='On Leave') |
                    Q(stat_1='Official Business')
                ).exclude(
                    Q(stat_4='Approved') |
                    Q(stat_4='Disapproved') |
                    Q(stat_4='Official Business') |
                    Q(stat_4='On Leave') |
                    Q(stat_1='Disapproved') |
                    Q(stat_1='Pending')
                ).order_by('-stat_4', '-updated_date')

                context = {'orders': orders2}
                return render(request, "display_letterardo.html", context)

            elif item1.aprover_1 == item.division_name:  # RCDS
                orders3 = Letter.objects.filter(
                    aprover_1=item.division_name
                ).exclude(
                    Q(stat_1='Approved') |
                    Q(stat_1='Disapproved')
                ).order_by('-stat_1', '-updated_date')

                context = {'orders': orders3}
                return render(request, "display_letter1.html", context)

    # If no conditions matched, return a default response (redirect or render)
    return redirect('addletter')  # Redirect to a different page if no conditions match

"""
def displayletterRCDS(request):
   
    user = AddDivisionww.objects.filter(user=request.user)
    for item in user:
        orders1 = Letter.objects.filter(Q(aprover_1=item.division_name)|Q(aprover_2=item.division_name)|Q(aprover_3=item.division_name)|Q(aprover_4=item.division_name)|Q(sender=item.division_name))
        for item1 in orders1:
            
            #print('ss',item1.letter_desc)
            #print('division sa div',item.division_name)
            #print('division sa Letter',item1.aprover_3)
            #print('RCDS',item1.stat_1)
            #print('ARDA',item1.stat_2)
            #print('ARDO',item1.stat_4)
            #print('division sa Letter',item1.aprover_3)
            if item1.aprover_3==item.division_name and item1.stat_2!="Pending":#RD
                orders4=Letter.objects.filter(aprover_3=item.division_name)and Letter.objects.filter(stat_1='Approved')and Letter.objects.filter(Q(stat_2='Approved')|Q(stat_2='On Leave')|Q(stat_2='Official Business'))and Letter.objects.exclude(Q(stat_3='Approved')|Q(stat_1='Disapproved')|Q(stat_4='Disapproved')|Q(stat_2='Disapproved')|Q(stat_2='Pending')).order_by('-stat_3','-updated_date')
                #for item3 in orders4:
                    #print('ssa',item3.letter_desc)
                context ={'orders':orders4}
                return render(request,"display_letter1111.html",context)
            elif item1.aprover_2==item.division_name and item1.stat_4!="Pending":#ARDA
                orders2=Letter.objects.filter(aprover_2=item.division_name)and Letter.objects.filter(Q(stat_4='Approved')|Q(stat_4='On Leave')|Q(stat_4='Official Business'))and Letter.objects.exclude(Q(stat_2='Approved')|Q(stat_2='Disapproved')|Q(stat_2='On Leave')|Q(stat_2='Official Business')|Q(stat_4='Pending')).order_by('-stat_2','-updated_date')
                #for item2 in orders2:
                    #print('ssb',item2.letter_desc)
                context ={'orders':orders2}
                return render(request,"display_letter111.html",context)
            elif item1.aprover_4==item.division_name and  item1.stat_1!='Pending':#ARDO
                orders2=Letter.objects.filter(aprover_4=item.division_name)and Letter.objects.filter(Q(stat_1='Approved')|Q(stat_1='On Leave')|Q(stat_1='Official Business'))and Letter.objects.exclude(Q(stat_4='Approved')|Q(stat_4='Disapproved')|Q(stat_4='Official Business')|Q(stat_4='On Leave')|Q(stat_1='Disapproved')|Q(stat_1='Pending')).order_by('-stat_4','-updated_date')
                #for item2 in orders2:
                    #print('ssb',item2.letter_desc)
                context ={'orders':orders2}
                return render(request,"display_letterardo.html",context)
            
            elif item1.aprover_1==item.division_name:#RCDS
                orders3=Letter.objects.filter(aprover_1=item.division_name)and Letter.objects.exclude(Q(stat_1='Approved')|Q(stat_1='Disapproved')).order_by('-stat_1','-updated_date')
                #for item2 in orders3:

                    #print(orders3)

                    #c=sorted( orders3, key = operator.itemgetter('date_send') )

                context ={'orders':orders3}
                return render(request,"display_letter1.html",context)
            else:
                #print('WLAY PAREHO RD')
                return redirect('addletter')"""

    
@login_required(login_url='loginuser')
def displayletter(request):
    #user=AddDivisionww.objects.filter(user=request.user)
    #for item in user:
    now = timezone.now()#display latest 7 days
    seven_day_before = now - timedelta(days=7)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
    orders = Letter.objects.filter(Q(user=request.user,date_send__gte=seven_day_before)).order_by('-updated_date')
        
            
    context ={'orders':orders}
    return render(request,"display_letter11.html",context)

@login_required(login_url='loginuser')
def displaylettermore(request):
    #user=AddDivisionww.objects.filter(user=request.user)
    #for item in user:
    #now = timezone.now()#display latest 7 days
    #seven_day_before = now - timedelta(days=7)
    #start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
    orders = Letter.objects.filter(user=request.user).order_by('-updated_date')
        
            
    context ={'orders':orders}
    return render(request,"display_lettermore.html",context)



@login_required
def modal_view(request, id):
    #modal = Letter.objects.filter(id=id)
    modal = get_object_or_404(Letter, id=id)
    
    remarks = modal.comment_rcds
    remarks1 = "RCDS"
    #print ('RCDS',remarks)
    return render(request, "modal_display.html", locals())


@login_required
def modal_view_arda(request, id):
    #modal = Letter.objects.filter(id=id)
    modal = get_object_or_404(Letter, id=id)
    
    remarks = modal.comment_arda
    remarks1 = "ARDA"
    #print ('ARDA',remarks)
    return render(request, "modal_display.html", locals())


@login_required
def modal_view_ardo(request, id):
    #modal = Letter.objects.filter(id=id)
    modal = get_object_or_404(Letter, id=id)
    
    remarks = modal.comment_ardo
    remarks1 = "ARDO"
    #print ('ARDO',remarks)
    return render(request, "modal_display.html", locals())

@login_required
def modal_view_rd(request, id):
    #modal = Letter.objects.filter(id=id)
    modal = get_object_or_404(Letter, id=id)
    
    remarks = modal.comment_rd
    remarks1 = "RD"
    
    return render(request, "modal_display.html", locals())




def aboutus(request):
    """user_id = request.user.id
    return render(request, 'register_device.html', {'user_id': user_id})"""
    return render(request, 'register_device.html')


def refreshdata(request):
    forclaim=Forclaim.objects.all()
    for item1 in forclaim:
        application=Idapplication.objects.filter(transaction_no=item1.transaction_no).delete()
    return HttpResponseRedirect(reverse('displayid'))




#NEW MODULE FOR ADMIN
def displayidadmin(request):
    #id= ID.objects.all()
    id=AddID.objects.all()
    stat1=Forclaim.objects.all()
    for item in stat1:
        a=int(item.user)
        #b=int(item.transaction_no)
        stat1=ID.objects.filter(user_id=a)and ID.objects.filter(transaction_no=item.transaction_no)
        for item2 in stat1:
            status=item2.status
            #print(item2.user_id)
            item2.status="Completed"
            item2.date_printed=item.date_printed
            item2.save()
    context={
    'id1':id1,
    'id':id,
    }

    return render(request,'displayid.html',context)


#new module for admin
def displayidadmin(request):
    id= AddID.objects.all()
    #id1=Forclaim.objects.all()
    
            
    forclaim=ForclaimAdmin.objects.all()
    for item1 in forclaim:
        application=AddID.objects.filter(transaction_no=item1.transaction_no)
        for status in application:
            status.status="Completed"
            status.date_printed=item1.date_printed
            status.save()
    context={
    
    'id':id,
    }

    return render(request,'displayidAdmin.html',context)


            
def displayid(request):
    id= ID.objects.all()
    id1=Employee.objects.all()
    stat1=Forclaim.objects.all()
    for item in stat1:
        a=int(item.user)
        #b=int(item.transaction_no)
        stat1=ID.objects.filter(user_id=a)and ID.objects.filter(transaction_no=item.transaction_no)
        for item2 in stat1:
            status=item2.status
            #print(item2.user_id)
            item2.status="Completed"
            item2.date_printed=item.date_printed
            item2.save()
    context={
    'id1':id1,
    'id':id,
    }

    return render(request,'displayid.html',context)

def activeapplication(request):
    idapplication = User.objects.all()
    ss=Idapplication.objects.filter(user__in=idapplication)
        
    context={
        'employee':ss
    }
    return render(request,'activeapplication.html',context)

def index(request):
  return render(request,'index.html',{
    'room_name':"webid"
    })

def logoutuser(request):
    logout(request)
    messages.success(request,("You Were Log-out!!! "))
    return redirect('index')



def loginuser(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('addletter')
        else:
            messages.success(request,("Invalid Username or Password"))
            return redirect('loginuser')
            
    else:
        return render(request, 'loginuser.html',{})
    


@login_required(login_url='loginuser')
def addprofileimage(request):
    submitted = False
    if request.method == 'POST':

        if not Employee.objects.filter(user=request.user):
            profile = Employee()
            profile.user_id = request.user.id
            
            
            p_form = ProfilePicture(request.POST,request.FILES,instance=profile)
            #p_form.user_id=request.user.id
            if p_form.is_valid():
                p_form.save()
                
                messages.success(request,f'Your Account has been Updated1111123')
                return redirect('addletter')
        
        else:
        
            fish = Employee.objects.get(user=request.user)  
            p_form = ProfilePicture(request.POST,request.FILES,instance=fish)
     
    
            if p_form.is_valid():
                p_form.save()
                messages.success(request,f'Your Account has been Updated')
                return redirect('addletter')
           
    else:
        
        if not Employee.objects.filter(user=request.user.id):
        
            p_form = ProfilePicture(instance=request.user)
          
        else:
           
            fish = Employee.objects.get(user=request.user)       
            p_form = ProfilePicture(instance=fish)
         
            
            
    context= {
        
        'p_form':p_form,
    }

    return render(request,'changeprofile.html',context)

@login_required(login_url='loginuser')
def addletter(request):
    if request.method == "POST":
        form = AddLetter(request.POST, request.FILES)

        if form.is_valid():
            reg = form.save(commit=False)
            action_request = request.POST.get('actionrequest', '')

            uploaded_file = request.FILES.get('letter_pdf_file')
            if uploaded_file:
                mega = Mega()
                m = mega.login(os.environ.get('MEGA_EMAIL'), os.environ.get('MEGA_PASSWORD'))

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    for chunk in uploaded_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                # Find or create "Letter" folder
                files = m.get_files()
                folder_id = None
                for key, value in files.items():
                    if value['t'] == 1 and value['a']['n'] == 'Letter':
                        folder_id = key
                        break
                if not folder_id:
                    folder = m.create_folder('Letter')
                    folder_id = list(folder.values())[0]

                # Upload file
                uploaded = m.upload(tmp_path, folder_id, uploaded_file.name)

                # ✅ Extract real Mega file ID
                file_id = uploaded['f'][0]['h']
                print(file_id)

                reg.mega_file_id = file_id
                reg.letter_pdf = m.get_upload_link(uploaded)

                os.remove(tmp_path)

            # Uppercase fields
            reg.letter_desc = form.cleaned_data['letter_desc'].upper()
            reg.sender = form.cleaned_data['sender'].upper()

            # Approvers
            reg.aprover_1 = 'RCDS'
            reg.aprover_2 = 'ARDA'
            reg.aprover_3 = 'RD'
            reg.aprover_4 = 'ARDO'

            reg.user = request.user
            reg.bjmptrans_no = 'bjmpro13' + str(random.randint(1111111, 9999999))
            reg.action_request = action_request

            reg.save()
            messages.success(request, "Successfully Sent Letter!")
            return redirect('displayletter')
    else:
        form = AddLetter()

    return render(request, 'addletter.html', {'form': form})



'''
@login_required(login_url='loginuser')
def addletter(request):
    if request.method == "POST":
        form = AddLetter(request.POST, request.FILES)

        # Generate transaction number
        trans_no = 'bjmpro13' + str(random.randint(1111111, 9999999))

        if form.is_valid():
            reg = form.save(commit=False)

            # Clean & format data
            reg.letter_desc = form.cleaned_data['letter_desc'].upper()
            reg.sender = form.cleaned_data['sender'].upper()
            reg.aprover_1 = 'RCDS'
            reg.aprover_2 = 'ARDA'
            reg.aprover_3 = 'RD'
            reg.user = request.user
            reg.bjmptrans_no = trans_no

            # Handle action request
            reg.action_request = request.POST.get('actionrequest')

            # -------- MEGA UPLOAD --------
            pdf_file = request.FILES.get('letter_pdf')
            if pdf_file:
                temp_path = f"/tmp/{pdf_file.name}"

                # Save temporarily
                with open(temp_path, 'wb+') as f:
                    for chunk in pdf_file.chunks():
                        f.write(chunk)

                # Upload to MEGA
                mega = Mega()
                m = mega.login(
                    os.environ.get('MEGA_EMAIL'),
                    os.environ.get('MEGA_PASSWORD')
                )

                uploaded_file = m.upload(temp_path)
                mega_link = m.get_upload_link(uploaded_file)

                # Save link instead of file
                reg.letter_pdf = mega_link

                # Delete temp file
                os.remove(temp_path)

            # Save to DB
            reg.save()
            form.save_m2m()

            messages.success(request, "Successfully Sent Letter!")
            return redirect('displayletter')

    else:
        form = AddLetter()

    return render(request, 'addletter.html', {'form': form})'''


def registeruser(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        #profile_form = ProfileForm(request.POST) #JULY 21,2022
        #profile_form.user_id=request.user.id
        if form.is_valid():
            reg =form.save(commit=False)
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            a=string.capwords(first_name)
            b=string.capwords(last_name)
            reg.first_name=a
            reg.last_name=b
            reg.save()
            


            #form.save()
            #profile_form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request, user)
            messages.success(request,("Registration Successful!"))
            return redirect('addletter')
    else:
        form = RegisterUserForm()
        #profile_form = ProfileForm()
    return render(request,'registeruser.html',{'form':form},)



@login_required(login_url='loginuser')
def status(request):
    status = ID.objects.filter(user=request.user)
    status1 = Employee.objects.filter(user=request.user)

    context= {
        'status':status,
        'status1':status1
    }

    return render(request,"status.html",context)
    



def downloadidadmin(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=ID_Application.csv'
    writer= csv.writer(response)
    user = AddID.objects.filter(status='Pending')
    
    writer.writerow(['User ID','Full Name','Designation','ID Code','Birth Date','Address','Contact Person','Contact Person Address','Contact Number','Pictures','Signature','Barcode','SSS No.','TIN','Blood Type','ID Status','Employee Contact Number','Transaction No.'])
    for item in user:
        #details = Employee.objects.filter(user_id = item.id)
        #for item1 in details:
            #foridapplication=Idapplication.objects.filter(user_id=item1.user_id)
            #for item2 in foridapplication:
        a=item.midle_initial
        a1=a[0]
        b=str(item.id_pic)
        c=("\\"+chr(92)+"192.168.6.87"+chr(92)+"Users"+chr(92)+"epcc"+chr(92)+"epccid"+chr(92)+"media"+chr(92))
        d=str(item.signature)
        firstname=str(item.first_name)

        writer.writerow([item.id,firstname+" "+a1+". "+item.last_name+" "+item.name_extension,item.disignation,item.id_code,item.birth_date,item.address,item.contact_person,item.contact_person_address,item.contact_person_no,c+ b,c+d,"",item.sss_no,item.tin,item.blood_type,"",item.contact_person_no,item.transaction_no])


            
    return response


def downloadidapp(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=ID_Application.csv'
    writer= csv.writer(response)
    user = User.objects.all()
    
    writer.writerow(['User ID','Full Name','Designation','ID Code','Birth Date','Address','Contact Person','Contact Person Address','Contact Number','Pictures','Signature','Barcode','SSS No.','TIN','Blood Type','ID Status','Employee Contact Number','Transaction No.'])
    for item in user:
        details = Employee.objects.filter(user_id = item.id)
        for item1 in details:
            foridapplication=Idapplication.objects.filter(user_id=item1.user_id)
            for item2 in foridapplication:
                a=item1.midle_initial
                a1=a[0]
                b=str(item1.id_pic)
                c=("\\"+chr(92)+"192.168.6.87"+chr(92)+"Users"+chr(92)+"epcc"+chr(92)+"epccid"+chr(92)+"media"+chr(92))
                d=str(item1.signature)
                firstname=str(item.first_name)

                writer.writerow([item.id,firstname+" "+a1+". "+item.last_name+" "+item1.name_extension,item1.disignation,item1.id_code,item1.birth_date,item1.address,item1.contact_person,item1.contact_person_address,item1.contact_person_no,c+ b,c+d,"",item1.sss_no,item1.tin,item1.blood_type,"",item1.contact_person_no,item2.transaction_no])


            
    return response



#for admin module
def importidforclaimadmin(request):
    if request.method == 'POST':
        file_format = request.POST['file-format']
        fish_resource = ForclaimResourceAdmin()
        f=ForclaimAdmin.objects.all()
        dataset = Dataset()
        new_fish = request.FILES['importData']

        if file_format == 'CSV':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='csv')
            result = fish_resource.import_data(dataset, dry_run=True)   
            

          

        elif file_format == 'JSON':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='json')
            # Testing data import
            result = fish_resource.import_data(dataset, dry_run=True) 

        if not result.has_errors():
            # Import now
            fish_resource.import_data(dataset, dry_run=False)



    return render(request, 'importadmin.html')








def importidforclaim(request):
    if request.method == 'POST':
        file_format = request.POST['file-format']
        fish_resource = ForclaimResource()
        f=Forclaim.objects.all()
        dataset = Dataset()
        new_fish = request.FILES['importData']

        if file_format == 'CSV':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='csv')
            result = fish_resource.import_data(dataset, dry_run=True)   
            

          

        elif file_format == 'JSON':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='json')
            # Testing data import
            result = fish_resource.import_data(dataset, dry_run=True) 

        if not result.has_errors():
            # Import now
            fish_resource.import_data(dataset, dry_run=False)



    return render(request, 'import.html')


def importdeptanddesignation(request):
    if request.method == 'POST':
        file_format = request.POST['file-format']
        fish_resource = DeptandDesignationResource()
        #f=Forclaim.objects.all()
        dataset = Dataset()
        new_fish = request.FILES['importData']

        if file_format == 'CSV':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='csv')
            result = fish_resource.import_data(dataset, dry_run=True)   
           
            #print(dataset)
          

        elif file_format == 'JSON':
            imported_data = dataset.load(new_fish.read().decode('utf-8'),format='json')
            # Testing data import
            result = fish_resource.import_data(dataset, dry_run=True) 

        if not result.has_errors():
            # Import now
            fish_resource.import_data(dataset, dry_run=False)

    return render(request, 'importdeptanddesignation.html')

#admin module
def reapplyid(request,id):
    submitted = False
    print(id)
    if request.method == 'POST':


        #ids = AddID.objects.get(id=id)
        reapply_form = AddDivision(request.POST,request.FILES)

    
        if reapply_form.is_valid():
            reapply_form.save()
           
            messages.success(request,f'Successfully Re Apply ID')
            return redirect('displayidadmin')
    else:
            ids = AddID.objects.get(id=id)       
            reapply_form = AddIDForm(instance=ids)

           
    ids = AddID.objects.get(id=id)
    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'reapplyid.html',context)






def updateremarks(request, id):
    submitted = False
    if request.method == 'POST':


        fish = ID.objects.get(user_id=id)
        fish_form = UpdateIDForm(request.POST,request.FILES,instance=fish)

    
        if fish_form.is_valid():
            fish_form.save()
           
            messages.success(request,f'Successfully Add Remarks')
            return redirect('buy')
    else:
            fish = ID.objects.get(user_id=id)       
            fish_form = UpdateIDForm(instance=fish)

           
    fish = ID.objects.get(user_id=id)
    context= {
        'fish_form':fish_form
        
        
    }

    return render(request,'updateremarks.html',context)


#new admin module
def updateremarks1admin(request, id):
    mymember = AddID.objects.get(id=id)
    template = loader.get_template('updateremarks1admin.html')
    context ={
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


def updateremarks1(request, id):
    mymember = ID.objects.get(id=id)
    template = loader.get_template('updateremarks1.html')
    context ={
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))


def updaterecordadmin(request,id):
    #first = request.POST['first']
    remarks = request.POST['remarks']
    member = AddID.objects.get(id=id)
    member.remarks = remarks
    
    member.save()
    return HttpResponseRedirect(reverse('displayidadmin'))



def updaterecord(request,id):
    #first = request.POST['first']
    remarks = request.POST['remarks']
    member = ID.objects.get(id=id)
    member.remarks = remarks
    
    member.save()
    return HttpResponseRedirect(reverse('displayid'))


#for admin module
def searchidapplicationadmin(request):
    if request.method == "POST":
        searched = request.POST['searched']
        h=string.capwords(searched)
       
        idapplication = AddID.objects.filter(first_name__contains=h)or AddID.objects.filter(last_name__contains=h)or AddID.objects.filter(midle_initial__contains=h)or AddID.objects.filter(status__contains=h)
        #ss=ID.objects.filter(user__in=idapplication)
        
        context={
            'idapplication':idapplication
        }
        return render(request,'searchidapplicationadmin.html',context)
    else:
        return render(request,'searchidapplicationadmin.html',{})


def searchidapplication(request):
    if request.method == "POST":
        searched = request.POST['searched']
        h=string.capwords(searched)
       
        idapplication = User.objects.filter(first_name__contains=h)or User.objects.filter(last_name__contains=h)
        ss=ID.objects.filter(user__in=idapplication)
        
        context={
            'idapplication':ss
        }
        return render(request,'searchidapplication.html',context)
    else:
        return render(request,'searchidapplication.html',{})





def addid(request):
    submitted = False
    if request.method == "POST":
        id_form = AddIDForm(request.POST,request.FILES)


        #if form.is_valid():
           # form.save()
            #return HttpResponseRedirect('/addfish2?submitted=True')
            #return HttpResponseRedirect(reverse('buy'))
            #return HttpResponseRedirect('/addfish2')


        print('sulod')
        if id_form.is_valid():
                print('next sulod')

                
                post = id_form.save(commit=False)
                #post1= u_form.save(commit=False)
                data = id_form.cleaned_data
                #data1=u_form.cleaned_data
                id_code = data['id_code']


                first_name=data['first_name']
                midle_initial=data['midle_initial']
                name_extension=data['name_extension']
                a=string.capwords(midle_initial)
                a1=a[0]
                last_name=data['last_name']
                name=first_name+" "+a1+"."+" "+last_name+name_extension
                print(name)
                oldname=DeptandDesignation.objects.filter(fullname=name)
                print(oldname)




                trans_no='klay45'+str(random.randint(1111111,9999999))
                while ID.objects.filter(transaction_no=trans_no)is None:
                    track='klay45'+str(random.randint(1111111,9999999))
                #id_application.transaction_no=trans_no

                
                if id_code == "":
                    
                    
                    data=id_form.cleaned_data
                    
                    designation = data['disignation']
                    print("pass de")


                    if DeptandDesignation.objects.filter(fullname=name):
                        print(name)

                        oldname=DeptandDesignation.objects.filter(fullname=name)
                        for nn in oldname:
                            print(nn.fullname)

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        #blood_type=data['blood_type']
                        first_name=data['first_name']
                        last_name=data['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        #f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)


                        post.id_code = nn.idcode
                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        #post.blood_type=f
                        post.first_name=g
                        post.last_name=h
                        post.transaction_no=trans_no
                        #print("trans_no")

                        post.save()
                        #post1.save()

                        #id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('addid')



                    else:
                        if designation =="IT Staff" or designation=="IT Technician" or designation=="OIC, MIS Section":

                            idcode=Idcode()
                            idcode.department="MIS"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="MIS").latest('id_code')
                        #aa=Idcode.objects.filter() #and (Idcode.objects.latest('id_code')))
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="EPCC-MIS-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code


                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            #blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            #f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            #post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #print(id_application.employee)

                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID SHIT IT')
                  

                            return redirect('addid')

                        elif designation =="Service Driver" or designation=="Backhoe Operator" or designation=="Forklift Operator"or designation=="Aircon Technician" or designation=="Apprentice Auto-Electrician" or designation=="Asphalt Distributor Operator"or designation=="Asphalt Paver Operator"or designation=="Associate Area Supervisor"or designation=="Auto Aircon Electrician"or designation=="Auto Electrician"or designation=="Auto Paintor"or designation=="Backhoe Operator"or designation=="Barge Tender"or designation=="Battery Man"or designation=="Boat Captain"or designation=="Body Builder"or designation=="Boomtruck Driver"or designation=="Bulldozer Operator" or designation=="Calibrator Operator"or designation=="Canvasser"or designation=="Chief Mate"or designation=="Cold Milling Machine Operator"or designation=="Concrete Paver Operator"or designation=="Concrete Pumpcrete Operator"or designation=="Concrete Pumptruck Operator"or designation=="Crane Operator"or designation=="Crimping Machine Operator"or designation=="Diesel Hammer Operator"or designation=="Dumptruck Driver"or designation=="Electrical Section Supervisor"or designation=="Electrician"or designation=="Electronic Technician"or designation=="Equipment And Rental Billing Analyst"or designation=="Equipment Coordinator"or designation=="Equipment History Analyst"or designation=="Equipment Management Analyst"or designation=="Equipment Management Area Supervisor"or designation=="Equipment Monitoring Processor"or designation=="Equipment Rental Billing Analyst"or designation=="Equipment Service Analyst R13"or designation=="Equipment Service Processor"or designation=="Fuel Tanker Driver"or designation=="Generator Technician"or designation=="Helper"or designation=="Helper - Machine Shop"or designation=="Hydraulic Hammer Operator"or designation=="Industrial Electrician"or designation=="Junior Mechanic"or designation=="Leadman"or designation=="Lubeman"or designation=="Machine Shop Section Supervisor"or designation=="Machinist"or designation=="Machinist Helper"or designation=="Marine Equipment In-Charge"or designation=="Mini-Fuel Tanker Driver"or designation=="Mechanical Section Supervisor"or designation=="Mini-Dumptruck Driver"or designation=="Chief Mate"or designation=="Motorpool Maintenance Personnel"or designation=="Motorpool Supervisor (Iligan)"or designation=="Motorpool Technician"or designation=="Office Aide"or designation=="Painter"or designation=="Payloader Operator"or designation=="Permits And Licensing Officer"or designation=="Power Tool Technician"or designation=="Preventive Maintenance Compliance Officer"or designation=="Prime Mover Driver"or designation=="Pumpboat Operator"or designation=="Quarter Master"or designation=="Radiator Maintenance"or designation=="Refinery Machine Operator"or designation=="Rigger"or designation=="Road Grader Operator"or designation=="Road Roller Operator"or designation=="Self Loader Driver"or designation=="Senior Electrician"or designation=="Service Advisor"or designation=="Service Advisor Processor"or designation=="Service Driver"or designation=="Shuttle Bus Driver"or designation=="Stake Truck Driver"or designation=="Tender"or designation=="Tireman"or designation=="Transit Mixer Driver"or designation=="Vibro Hammer Operator"or designation=="Water Truck Driver"or designation=="Welder"or designation=="Welding Section Supervisor":
                        #code ='EMD'+str(random.randint(1111111,9999999))

                            idcode=Idcode()
                            idcode.department="EMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="EMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-EMD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code


                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('addid')
                            




                        elif designation =="Drilling Operator" or designation=="Field Engineer" or designation=="Geodetic Engineer"or designation=="Instrument Man"or designation=="Junior Project Manager"or designation=="Office Assistant"or designation=="Paving Block Operator/In-Charge"or designation=="Project Accounting Processor"or designation=="Project Accounting Supervisor"or designation=="Project Engineer"or designation=="Project Processor"or designation=="Survey Aide"or designation=="Surveyor":
                        #code ='EMD'+str(random.randint(1111111,9999999))

                            idcode=Idcode()
                            idcode.department="PMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="PMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-ENG-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Company Nurse"or designation=="Project Nurse" or designation=="First Aider" or designation=="Safety And Health Division Head"or designation=="Safety And Health Processor"or designation=="Safety Officer"or designation=="Administrative Support Processor"or designation=="Billing Processor"or designation=="GPS/CCTV Maintenance"or designation=="GSD Processor"or designation=="Internal Security"or designation=="Office Utility"or designation=="OIC, Facilities Maintenance Section"or designation=="Permits And Licenses Processor"or designation=="Records Custodian"or designation=="Security Processor"or designation=="Security Section Supervisor"or designation=="Tarpaulin Production Assistant"or designation=="Truck Master":
                            idcode=Idcode()
                            idcode.department="GSD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="GSD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-GSD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Accounting Analyst" or designation=="Accounting Processor" or designation=="Accounts Payable Billing Processor"or designation=="Accounts Payable Clerk II"or designation=="Accounts Payable Disbursement Clerk II"or designation=="Administrative Support Processor"or designation=="Accounts Payable Section Supervisor R13"or designation=="Accounts Receivable Processor"or designation=="Accounts Receivables Section Supervisor"or designation=="AP Billing Bookkeeper"or designation=="AP Billing Clerk"or designation=="AP Billing Processor"or designation=="AP Disbursement Bookkeeper"or designation=="AP Disbursement Clerk"or designation=="AP Disbursement Clerk (Aide)"or designation=="AP Disbursement Processor"or designation=="Asset Account Processor"or designation=="Bookkeeper"or designation=="Bookkeeper III"or designation=="Compliance Bookkeeper"or designation=="Compliance Clerk II"or designation=="Disbursement Clerk"or designation=="Disbursement Clerk II"or designation=="OIC, Accounts Payable Section R10"or designation=="Reconciliation Processor":
                            idcode=Idcode()
                            idcode.department="Accounting"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Accounting").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="FIN-ACT-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Collection Processor" or designation=="Collection Section Supervisor" or designation=="Disbursement And Collection Processor"or designation=="Disbursement And Collection Supervisor"or designation=="Disbursement Processor"or designation=="Disbursing Supervisor R10"or designation=="Disbursing Supervisor R13"or designation=="Office Cashier"or designation=="Treasury Aide"or designation=="Treasury Processor":
                            idcode=Idcode()
                            idcode.department="Treasury"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Treasury").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="FIN-TRE-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Compensation And Benefits Processor" or designation=="Employee Relations Processor" or designation=="HR Assistant"or designation=="Human Resource Generalist"or designation=="OIC, Compensation And Benefits Section"or designation=="OIC, Employee Relations Section"or designation=="Records In-Charge"or designation=="Recruitment And Hiring Processor"or designation=="Recruitment And Hiring Section Supervisor"or designation=="Training And Development Section Supervisor"or designation=="Training Associate":
                            idcode=Idcode()
                            idcode.department="Human Resource"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Human Resource").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-HRD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Gasman" or designation=="Inventory Management Requisition Analyst" or designation=="Inventory Withdrawal Processor"or designation=="Stock Analyst"or designation=="IMD Reception"or designation=="Inventory Management Withdrawal Analyst (Central/Project)"or designation=="Inventory Variance Report Processor"or designation=="Toolkeeper"or designation=="IMD-Junior Parts Specialist"or designation=="OIC, Inventory Management Section 13"or designation=="Inventory Management Stock Analyst"or designation=="Materials Receiving Processor"or designation=="Inventory Management Withdrawal Analyst (Project)"or designation=="Inventory Management Parts Specialist"or designation=="Lube Stockman"or designation=="Inventory Management Withdrawal Encoder - Central"or designation=="Inventory Management Receiving Analyst"or designation=="Inventory Management Control Specialist"or designation=="Inventory Management Processor"or designation=="Inventory Control Specialist"or designation=="Inventory Management Receiving Analyst (Project)"or designation=="OIC, Inventory Management Section R10"or designation=="Receiving Analyst"or designation=="Warehouse Tender"or designation=="Inventory Management Withdrawal Analyst":
                            idcode=Idcode()
                            idcode.department="IMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="IMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-IMD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')

                        elif designation =="Bidding And Contracts Officer" or designation =="Bidding And Contracts Processor" or designation =="Contract Handling Processor" or designation =="Marketing Aide" or designation =="Office Engineer" or designation =="OIC, Contracts And Handling Section" or designation =="OIC, Special License Handling Section" or designation =="Special License Compliance Processor":
                            idcode=Idcode()
                            idcode.department="Marketing"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Marketing").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="MTG-MBD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Billing Aide" or designation =="Billing Officer" or designation =="Billing Section Supervisor R10" or designation =="Cadd Operator" or designation =="Civil 3D Operator" or designation =="Cost Engineer" or designation =="Monitoring Engineer" or designation =="OIC, Billing Section R13" or designation =="Project Monitoring Section Supervisor" or designation =="Quantity Engineer" or designation =="Technical Assistant" or designation =="Technical Engineer" or designation =="Technical Officer" or designation =="Technical Services Processor":
                            idcode=Idcode()
                            idcode.department="TSD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="TSD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ENG-TSD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Canvassing Processor"or designation =="Purchaser" or designation =="Procurement Processor" or designation =="Purchasing Processor" or designation =="Records Processor" or designation =="OIC, Canvassing Division R13" or designation =="OIC, Canvassing Section R10" or designation =="PO Processor" or designation =="Procurement Analyst R10" or designation =="Canvassing Proccesor" or designation =="Turn-Over Processor" or designation =="Procurement Analyst R13" or designation =="OIC, Logistics Section R13" or designation =="Canvassing Processor R13" or designation =="Procurement Processor R13":
                            idcode=Idcode()
                            idcode.department="PROCUREMENT"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="PROCUREMENT").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-LOG-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Accounting And Recording Audit Supervisor" or designation =="Document Controller" or designation =="Document Custodian" or designation =="Field Auditor" or designation =="Internal Audit System Assistant" or designation =="Internal Control Financial Reporting Division Head" or designation =="OIC, IAS QMS Section" or designation =="QMS Assistant":
                            idcode=Idcode()
                            idcode.department="IAS"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="IAS").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="IAS-QMS-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Asphalt Heating Operator" or designation =="Assistant Plant Operator"or designation =="Checker"or designation =="Clerical Processor"or designation =="Compliance Section Supervisor"or designation =="Foreman"or designation =="Heating Operator"or designation =="Mining Engineer"or designation =="Plant Account Analyst"or designation =="Plant Aide"or designation =="Plant Electrician"or designation =="Plant Maintenance"or designation =="Plant Operator"or designation =="Plant Processor"or designation =="Plant Supervisor"or designation =="Plant Technician"or designation =="Plants Processor"or designation =="Project Cashier"or designation =="Project Safety Aide"or designation =="Social Development Officer"or designation =="Truckscale Operator":
                            idcode=Idcode()
                            idcode.department="Production"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Production").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-PROD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Chemical Laboratory Supervisor" or designation =="Chemist" or designation =="Laboratory Aide" or designation =="Laboratory Technician" or designation =="Materials Assistant" or designation =="Materials Engineer" or designation =="Physical Labortory Supervisor" or designation =="Quality Control Engineer":
                            idcode=Idcode()
                            idcode.department="Materials Quality Control"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Materials Quality Control").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-QC-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data['first_name']
                            last_name=data['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)



                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post.first_name=g
                            post.last_name=h
                            post.transaction_no=trans_no

                            post.save()
                            #post1.save()
                            #id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')

                else:
                    if not DeptandDesignation.objects.filter(fullname=name):

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        blood_type=data['blood_type']
                        first_name=data['first_name']
                        last_name=data['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)
                        print("walay match")
                        print(name)

                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        post.blood_type=f
                        post.first_name=g
                        post.last_name=h
                        post.transaction_no=trans_no

                        post.save()
                        #post1.save()

                        #id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('status')

                    else:

                        oldname=DeptandDesignation.objects.filter(fullname=name)
                        for nn in oldname:
                                print(nn.fullname)

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        blood_type=data['blood_type']
                        first_name=data['first_name']
                        last_name=data['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)

                        post.id_code = nn.idcode
                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        post.blood_type=f
                        post.first_name=g
                        post.last_name=h
                        post.transaction_no=trans_no

                        post.save()
                        #post1.save()


                        #id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('status')




    else:
        id_form = AddIDForm()
        #id_form = AddIDForm(request.POST,request.FILES)

    context= {
        'id_form':id_form,
   
    }

    return render(request,'addid.html',context)


@login_required(login_url='loginuser')
def profile(request):
    submitted = False
    if request.method == 'POST':

        if not Employee.objects.filter(user=request.user.id):
            employee = Employee()
            employee.user_id = request.user.id
            id_application= ID()
            id_application.user = request.user


            trans_no='klay45'+str(random.randint(1111111,9999999))
            while ID.objects.filter(transaction_no=trans_no)is None:
                track='klay45'+str(random.randint(1111111,9999999))
            id_application.transaction_no=trans_no
            
            
            u_form = UserUpdateForm(request.POST,instance=request.user)
            p_form = ProfileUpdateForm(request.POST,request.FILES, instance=employee)


            if not Idapplication.objects.filter(user=request.user):
                foridapplication=Idapplication()
                foridapplication.user=request.user

                foridapplication.transaction_no=trans_no
                foridapplication.save()





            if p_form.is_valid() and u_form.is_valid():

                
                post = p_form.save(commit=False)
                post1= u_form.save(commit=False)
                data = p_form.cleaned_data
                data1=u_form.cleaned_data
                id_code = data['id_code']


                first_name=data1['first_name']
                midle_initial=data['midle_initial']
                name_extension=data['name_extension']
                a=string.capwords(midle_initial)
                a1=a[0]
                last_name=data1['last_name']
                name=first_name+" "+a1+"."+" "+last_name+" "+name_extension
                oldname=DeptandDesignation.objects.filter(fullname=name)
                print(oldname)

                
                if id_code == "":
                    
                    
                    data1=u_form.cleaned_data
                    
                    designation = data['disignation']
                    print("pass")


                    if DeptandDesignation.objects.filter(fullname=name):

                        oldname=DeptandDesignation.objects.filter(fullname=name)
                        for nn in oldname:
                            print(nn.fullname)

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        #blood_type=data['blood_type']
                        first_name=data1['first_name']
                        last_name=data1['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        #f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)


                        post.id_code = nn.idcode
                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        #post.blood_type=f
                        post1.first_name=g
                        post1.last_name=h

                        post.save()
                        post1.save()

                        id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('status')



                    else:
                        if designation =="IT Staff" or designation=="IT Technician" or designation=="OIC, MIS Section":

                            idcode=Idcode()
                            idcode.department="MIS"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="MIS").latest('id_code')
                        #aa=Idcode.objects.filter() #and (Idcode.objects.latest('id_code')))
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="EPCC-MIS-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code


                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            #blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            #f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            #post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            #print(id_application.employee)

                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID SHIT IT')
                  

                            return redirect('status')

                        elif designation =="Service Driver" or designation=="Backhoe Operator" or designation=="Forklift Operator"or designation=="Aircon Technician" or designation=="Apprentice Auto-Electrician" or designation=="Asphalt Distributor Operator"or designation=="Asphalt Paver Operator"or designation=="Associate Area Supervisor"or designation=="Auto Aircon Electrician"or designation=="Auto Electrician"or designation=="Auto Paintor"or designation=="Backhoe Operator"or designation=="Barge Tender"or designation=="Battery Man"or designation=="Boat Captain"or designation=="Body Builder"or designation=="Boomtruck Driver"or designation=="Bulldozer Operator" or designation=="Calibrator Operator"or designation=="Canvasser"or designation=="Chief Mate"or designation=="Cold Milling Machine Operator"or designation=="Concrete Paver Operator"or designation=="Concrete Pumpcrete Operator"or designation=="Concrete Pumptruck Operator"or designation=="Crane Operator"or designation=="Crimping Machine Operator"or designation=="Diesel Hammer Operator"or designation=="Dumptruck Driver"or designation=="Electrical Section Supervisor"or designation=="Electrician"or designation=="Electronic Technician"or designation=="Equipment And Rental Billing Analyst"or designation=="Equipment Coordinator"or designation=="Equipment History Analyst"or designation=="Equipment Management Analyst"or designation=="Equipment Management Area Supervisor"or designation=="Equipment Monitoring Processor"or designation=="Equipment Rental Billing Analyst"or designation=="Equipment Service Analyst R13"or designation=="Equipment Service Processor"or designation=="Fuel Tanker Driver"or designation=="Generator Technician"or designation=="Helper"or designation=="Helper - Machine Shop"or designation=="Hydraulic Hammer Operator"or designation=="Industrial Electrician"or designation=="Junior Mechanic"or designation=="Leadman"or designation=="Lubeman"or designation=="Machine Shop Section Supervisor"or designation=="Machinist"or designation=="Machinist Helper"or designation=="Marine Equipment In-Charge"or designation=="Mini-Fuel Tanker Driver"or designation=="Mechanical Section Supervisor"or designation=="Mini-Dumptruck Driver"or designation=="Chief Mate"or designation=="Motorpool Maintenance Personnel"or designation=="Motorpool Supervisor (Iligan)"or designation=="Motorpool Technician"or designation=="Office Aide"or designation=="Painter"or designation=="Payloader Operator"or designation=="Permits And Licensing Officer"or designation=="Power Tool Technician"or designation=="Preventive Maintenance Compliance Officer"or designation=="Prime Mover Driver"or designation=="Pumpboat Operator"or designation=="Quarter Master"or designation=="Radiator Maintenance"or designation=="Refinery Machine Operator"or designation=="Rigger"or designation=="Road Grader Operator"or designation=="Road Roller Operator"or designation=="Self Loader Driver"or designation=="Senior Electrician"or designation=="Service Advisor"or designation=="Service Advisor Processor"or designation=="Service Driver"or designation=="Shuttle Bus Driver"or designation=="Stake Truck Driver"or designation=="Tender"or designation=="Tireman"or designation=="Transit Mixer Driver"or designation=="Vibro Hammer Operator"or designation=="Water Truck Driver"or designation=="Welder"or designation=="Welding Section Supervisor":
                        #code ='EMD'+str(random.randint(1111111,9999999))

                            idcode=Idcode()
                            idcode.department="EMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="EMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-EMD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code


                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')
                            




                        elif designation =="Drilling Operator" or designation=="Field Engineer" or designation=="Geodetic Engineer"or designation=="Instrument Man"or designation=="Junior Project Manager"or designation=="Office Assistant"or designation=="Paving Block Operator/In-Charge"or designation=="Project Accounting Processor"or designation=="Project Accounting Supervisor"or designation=="Project Engineer"or designation=="Project Processor"or designation=="Survey Aide"or designation=="Surveyor":
                        #code ='EMD'+str(random.randint(1111111,9999999))

                            idcode=Idcode()
                            idcode.department="PMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="PMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-ENG-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Company Nurse"or designation=="Project Nurse" or designation=="First Aider" or designation=="Safety And Health Division Head"or designation=="Safety And Health Processor"or designation=="Safety Officer"or designation=="Administrative Support Processor"or designation=="Billing Processor"or designation=="GPS/CCTV Maintenance"or designation=="GSD Processor"or designation=="Internal Security"or designation=="Office Utility"or designation=="OIC, Facilities Maintenance Section"or designation=="Permits And Licenses Processor"or designation=="Records Custodian"or designation=="Security Processor"or designation=="Security Section Supervisor"or designation=="Tarpaulin Production Assistant"or designation=="Truck Master":
                            idcode=Idcode()
                            idcode.department="GSD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="GSD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-GSD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Accounting Analyst" or designation=="Accounting Processor" or designation=="Accounts Payable Billing Processor"or designation=="Accounts Payable Clerk II"or designation=="Accounts Payable Disbursement Clerk II"or designation=="Administrative Support Processor"or designation=="Accounts Payable Section Supervisor R13"or designation=="Accounts Receivable Processor"or designation=="Accounts Receivables Section Supervisor"or designation=="AP Billing Bookkeeper"or designation=="AP Billing Clerk"or designation=="AP Billing Processor"or designation=="AP Disbursement Bookkeeper"or designation=="AP Disbursement Clerk"or designation=="AP Disbursement Clerk (Aide)"or designation=="AP Disbursement Processor"or designation=="Asset Account Processor"or designation=="Bookkeeper"or designation=="Bookkeeper III"or designation=="Compliance Bookkeeper"or designation=="Compliance Clerk II"or designation=="Disbursement Clerk"or designation=="Disbursement Clerk II"or designation=="OIC, Accounts Payable Section R10"or designation=="Reconciliation Processor":
                            idcode=Idcode()
                            idcode.department="Accounting"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Accounting").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="FIN-ACT-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Collection Processor" or designation=="Collection Section Supervisor" or designation=="Disbursement And Collection Processor"or designation=="Disbursement And Collection Supervisor"or designation=="Disbursement Processor"or designation=="Disbursing Supervisor R10"or designation=="Disbursing Supervisor R13"or designation=="Office Cashier"or designation=="Treasury Aide"or designation=="Treasury Processor":
                            idcode=Idcode()
                            idcode.department="Treasury"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Treasury").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="FIN-TRE-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Compensation And Benefits Processor" or designation=="Employee Relations Processor" or designation=="HR Assistant"or designation=="Human Resource Generalist"or designation=="OIC, Compensation And Benefits Section"or designation=="OIC, Employee Relations Section"or designation=="Records In-Charge"or designation=="Recruitment And Hiring Processor"or designation=="Recruitment And Hiring Section Supervisor"or designation=="Training And Development Section Supervisor"or designation=="Training Associate":
                            idcode=Idcode()
                            idcode.department="Human Resource"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Human Resource").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-HRD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Gasman" or designation=="Inventory Management Requisition Analyst" or designation=="Inventory Withdrawal Processor"or designation=="Stock Analyst"or designation=="IMD Reception"or designation=="Inventory Management Withdrawal Analyst (Central/Project)"or designation=="Inventory Variance Report Processor"or designation=="Toolkeeper"or designation=="IMD-Junior Parts Specialist"or designation=="OIC, Inventory Management Section 13"or designation=="Inventory Management Stock Analyst"or designation=="Materials Receiving Processor"or designation=="Inventory Management Withdrawal Analyst (Project)"or designation=="Inventory Management Parts Specialist"or designation=="Lube Stockman"or designation=="Inventory Management Withdrawal Encoder - Central"or designation=="Inventory Management Receiving Analyst"or designation=="Inventory Management Control Specialist"or designation=="Inventory Management Processor"or designation=="Inventory Control Specialist"or designation=="Inventory Management Receiving Analyst (Project)"or designation=="OIC, Inventory Management Section R10"or designation=="Receiving Analyst"or designation=="Warehouse Tender"or designation=="Inventory Management Withdrawal Analyst":
                            idcode=Idcode()
                            idcode.department="IMD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="IMD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-IMD-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')

                        elif designation =="Bidding And Contracts Officer" or designation =="Bidding And Contracts Processor" or designation =="Contract Handling Processor" or designation =="Marketing Aide" or designation =="Office Engineer" or designation =="OIC, Contracts And Handling Section" or designation =="OIC, Special License Handling Section" or designation =="Special License Compliance Processor":
                            idcode=Idcode()
                            idcode.department="Marketing"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Marketing").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="MTG-MBD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Billing Aide" or designation =="Billing Officer" or designation =="Billing Section Supervisor R10" or designation =="Cadd Operator" or designation =="Civil 3D Operator" or designation =="Cost Engineer" or designation =="Monitoring Engineer" or designation =="OIC, Billing Section R13" or designation =="Project Monitoring Section Supervisor" or designation =="Quantity Engineer" or designation =="Technical Assistant" or designation =="Technical Engineer" or designation =="Technical Officer" or designation =="Technical Services Processor":
                            idcode=Idcode()
                            idcode.department="TSD"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="TSD").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ENG-TSD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Canvassing Processor"or designation =="Purchaser" or designation =="Procurement Processor" or designation =="Purchasing Processor" or designation =="Records Processor" or designation =="OIC, Canvassing Division R13" or designation =="OIC, Canvassing Section R10" or designation =="PO Processor" or designation =="Procurement Analyst R10" or designation =="Canvassing Proccesor" or designation =="Turn-Over Processor" or designation =="Procurement Analyst R13" or designation =="OIC, Logistics Section R13" or designation =="Canvassing Processor R13" or designation =="Procurement Processor R13":
                            idcode=Idcode()
                            idcode.department="PROCUREMENT"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="PROCUREMENT").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="ADM-LOG-"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Accounting And Recording Audit Supervisor" or designation =="Document Controller" or designation =="Document Custodian" or designation =="Field Auditor" or designation =="Internal Audit System Assistant" or designation =="Internal Control Financial Reporting Division Head" or designation =="OIC, IAS QMS Section" or designation =="QMS Assistant":
                            idcode=Idcode()
                            idcode.department="IAS"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="IAS").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="IAS-QMS-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')


                        elif designation =="Asphalt Heating Operator" or designation =="Assistant Plant Operator"or designation =="Checker"or designation =="Clerical Processor"or designation =="Compliance Section Supervisor"or designation =="Foreman"or designation =="Heating Operator"or designation =="Mining Engineer"or designation =="Plant Account Analyst"or designation =="Plant Aide"or designation =="Plant Electrician"or designation =="Plant Maintenance"or designation =="Plant Operator"or designation =="Plant Processor"or designation =="Plant Supervisor"or designation =="Plant Technician"or designation =="Plants Processor"or designation =="Project Cashier"or designation =="Project Safety Aide"or designation =="Social Development Officer"or designation =="Truckscale Operator":
                            idcode=Idcode()
                            idcode.department="Production"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Production").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-PROD-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)

                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')



                        elif designation =="Chemical Laboratory Supervisor" or designation =="Chemist" or designation =="Laboratory Aide" or designation =="Laboratory Technician" or designation =="Materials Assistant" or designation =="Materials Engineer" or designation =="Physical Labortory Supervisor" or designation =="Quality Control Engineer":
                            idcode=Idcode()
                            idcode.department="Materials Quality Control"
                            idcode.user_id=request.user.id
                            a=Idcode.objects.filter(department="Materials Quality Control").latest('id_code')
                            b=a.id_code
                            c=b.split("-")
                            d=c[-1]
                            f=int(d)
                            g=f+1
                            h=str(g)
                            code="OPR-QC-0"+h
                            idcode.id_code=code
                            idcode.save()

                            post.id_code=code



                            contact_person_address=data['contact_person_address']
                            midle_initial=data['midle_initial']
                            address=data['address']
                            name_extension=data['name_extension']
                            contact_person=data['contact_person']
                            blood_type=data['blood_type']
                            first_name=data1['first_name']
                            last_name=data1['last_name']


                            a=string.capwords(contact_person_address)
                            b=string.capwords(midle_initial)
                            c=string.capwords(address)
                            d=string.capwords(name_extension)
                            e=string.capwords(contact_person)
                            f=string.capwords(blood_type)
                            g=string.capwords(first_name)
                            h=string.capwords(last_name)



                            post.first_name=g
                            post.last_name=h
                            post.contact_person_address=a
                            post.midle_initial=b
                            post.address=c
                            post.name_extension=d
                            post.contact_person=e
                            post.blood_type=f
                            post1.first_name=g
                            post1.last_name=h

                            post.save()
                            post1.save()
                            id_application.save()
                            messages.success(request,f'Successfully Apply for ID')
                            return redirect('status')

                else:
                    if not DeptandDesignation.objects.filter(fullname=name):

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        blood_type=data['blood_type']
                        first_name=data1['first_name']
                        last_name=data1['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)
                        print("walay match")
                        print(name)

                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        post.blood_type=f
                        post1.first_name=g
                        post1.last_name=h

                        post.save()
                        post1.save()

                        id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('status')

                    else:

                        oldname=DeptandDesignation.objects.filter(fullname=name)
                        for nn in oldname:
                                print(nn.fullname)

                        contact_person_address=data['contact_person_address']
                        midle_initial=data['midle_initial']
                        address=data['address']
                        name_extension=data['name_extension']
                        contact_person=data['contact_person']
                        blood_type=data['blood_type']
                        first_name=data1['first_name']
                        last_name=data1['last_name']


                        a=string.capwords(contact_person_address)
                        b=string.capwords(midle_initial)
                        c=string.capwords(address)
                        d=string.capwords(name_extension)
                        e=string.capwords(contact_person)
                        f=string.capwords(blood_type)
                        g=string.capwords(first_name)
                        h=string.capwords(last_name)

                        post.id_code = nn.idcode
                        post.first_name=g
                        post.last_name=h
                        post.contact_person_address=a
                        post.midle_initial=b
                        post.address=c
                        post.name_extension=d
                        post.contact_person=e
                        post.blood_type=f
                        post1.first_name=g
                        post1.last_name=h

                        post.save()
                        post1.save()


                        id_application.save()
                        messages.success(request,f'Successfully Apply for ID SHIT')
                        return redirect('status')

        else:
            if not Idapplication.objects.filter(user=request.user):
                foridapplication=Idapplication()
                foridapplication.user=request.user
                trans_no='klay45'+str(random.randint(1111111,9999999))
                foridapplication.transaction_no=trans_no
                foridapplication.save()
                
                print("sa elese ni")


                id_application= ID()
                id_application.user = request.user
                id_application.transaction_no=trans_no
                id_application.save()

        
            

            u_form = UserUpdateForm(request.POST,instance=request.user)

            p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.employee)
         
            




    
            if p_form.is_valid() and u_form.is_valid():
                post = p_form.save(commit=False)
                post1 = u_form.save(commit=False)
                data = p_form.cleaned_data
                data1 = u_form.cleaned_data


                first_name=data1['first_name']
                midle_initial=data['midle_initial']
                name_extension=data['name_extension']
                a=string.capwords(midle_initial)
                a1=a[0]
                last_name=data1['last_name']
                name=first_name+" "+a1+"."+" "+last_name+name_extension
                if not DeptandDesignation.objects.filter(fullname=name):
               
                    contact_person_address=data['contact_person_address']
                    midle_initial=data['midle_initial']
                    address=data['address']
                    name_extension=data['name_extension']
                    contact_person=data['contact_person']
                    #blood_type=data['blood_type']
                    first_name=data1['first_name']
                    last_name=data1['last_name']

                    a=string.capwords(contact_person_address)
                    b=string.capwords(midle_initial)
                    c=string.capwords(address)
                    d=string.capwords(name_extension)
                    e=string.capwords(contact_person)
                    #f=string.capwords(blood_type)
                    g=string.capwords(first_name)
                    h=string.capwords(last_name)

                    #post.id_code=nn.idcode
                    post.first_name=g
                    post.last_name=h
                    post.contact_person_address=a
                    post.midle_initial=b
                    post.address=c
                    post.name_extension=d
                    post.contact_person=e
                    #post.blood_type=f
                    post1.first_name=g
                    post1.last_name=h

                    post.save()
                    post1.save()
                
                    messages.success(request,f'Your Account has been Updated')
                    return redirect('status')
                else:
                    oldname=DeptandDesignation.objects.filter(fullname=name)
                    for nn in oldname:
                        print(nn.fullname)



                    contact_person_address=data['contact_person_address']
                    midle_initial=data['midle_initial']
                    address=data['address']
                    name_extension=data['name_extension']
                    contact_person=data['contact_person']
                    #blood_type=data['blood_type']
                    first_name=data1['first_name']
                    last_name=data1['last_name']

                    a=string.capwords(contact_person_address)
                    b=string.capwords(midle_initial)
                    c=string.capwords(address)
                    d=string.capwords(name_extension)
                    e=string.capwords(contact_person)
                    #f=string.capwords(blood_type)
                    g=string.capwords(first_name)
                    h=string.capwords(last_name)

                    post.id_code=nn.idcode
                    post.first_name=g
                    post.last_name=h
                    post.contact_person_address=a
                    post.midle_initial=b
                    post.address=c
                    post.name_extension=d
                    post.contact_person=e
                    #post.blood_type=f
                    post1.first_name=g
                    post1.last_name=h

                    post.save()
                    post1.save()
                
                    messages.success(request,f'Your Account has been Updated')
                    return redirect('status')





    else:







        if not Employee.objects.filter(user=request.user.id):
            #ddd=DeptandDesignation.objects.all().values()
            u_form = UserUpdateForm(instance=request.user)

            p_form = ProfileUpdateForm()
            
        else:
            
            u_form = UserUpdateForm(instance=request.user)

            p_form = ProfileUpdateForm(instance=request.user.employee)
            #d_form = DeptandDesignationForm(instance=ddd)

    context= {
        'u_form':u_form,
        'p_form':p_form,
        #'d_form':d_form

    }

    return render(request,'userupdateform.html',context)



def registerdivision(request):
    if request.method == "POST":
        form = AddDivision(request.POST,instance=request.user)
        form.user_id = request.user
        #profile_form = ProfileForm(request.POST) #JULY 21,2022
        #profile_form.user_id=request.user.id
        if form.is_valid():
            reg =form.save(commit=False)
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            midle_initial=form.cleaned_data['midle_initial']
            a=string.capwords(first_name)
            b=string.capwords(last_name)
            c=string.capwords(midle_initial)
            reg.first_name=a
            reg.last_name=b
            reg.midle_initial=c
            reg.save()
            


            #form.save()
            #profile_form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request, user)
            messages.success(request,("Registration Successful!"))
            return redirect('index')
    else:
        form = AddDivision()
        #profile_form = ProfileForm()
    return render(request,'registerdivision.html',{'form':form},)



@login_required(login_url='loginuser')
def division1(request):
    submitted = False
    if request.method == 'POST':

        if not Employee.objects.filter(user=request.user.id):
            employee = DivisionOffice()
            employee.user_id = request.user.id

            
            
            #u_form = UserUpdateForm(request.POST,instance=request.user)
            p_form = AddDivision(request.POST,instance=request.user_id)



            if p_form.is_valid():

                
                post = p_form.save(commit=False)
                #post1= u_form.save(commit=False)
                data = p_form.cleaned_data
                data1=u_form.cleaned_data
                
                first_name=data1['first_name']
                midle_initial=data['midle_initial']
                name_extension=data['name_extension']
                a=string.capwords(midle_initial)
                a1=a[0]
                last_name=data1['last_name']
                name=first_name+" "+a1+"."+" "+last_name+" "+name_extension
                oldname=DeptandDesignation.objects.filter(fullname=name)
                print(oldname)


        else:
            if not Idapplication.objects.filter(user=request.user):
                foridapplication=Idapplication()
                foridapplication.user=request.user
                trans_no='klay45'+str(random.randint(1111111,9999999))
                foridapplication.transaction_no=trans_no
                foridapplication.save()
                
                print("sa elese ni")


                id_application= ID()
                id_application.user = request.user
                id_application.transaction_no=trans_no
                id_application.save()

        
            

            u_form = UserUpdateForm(request.POST,instance=request.user)

            p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.employee)
         


    else:

        if not Employee.objects.filter(user=request.user.id):
            #ddd=DeptandDesignation.objects.all().values()
            u_form = UserUpdateForm(instance=request.user)

            p_form = ProfileUpdateForm()
            
        else:
            
            u_form = UserUpdateForm(instance=request.user)

            p_form = ProfileUpdateForm(instance=request.user.employee)
            #d_form = DeptandDesignationForm(instance=ddd)

    context= {
        'u_form':u_form,
        'p_form':p_form,
        #'d_form':d_form

    }

    return render(request,'userupdateform.html',context)




def adddivision(request):
    submitted = False
    if request.method == "POST":
        form = AddDivisionForm(request.POST)
       
        if form.is_valid():
            form.save()
         
            
            messages.success(request,("Division Added!"))
            return redirect('index')
    else:
        form = AddDivisionForm()
       
    return render(request,'adddivision.html',{'form':form},)

@login_required(login_url='loginuser')
def adddivision1(request):
    submitted = False
    if request.method == 'POST':

        if not AddDivisionww.objects.filter(user_id=request.user):
            profile = AddDivisionww()
            profile.user_id = request.user.id
            
            u_form = UserUpdateForm(request.POST,instance=request.user)
            #p_form = AddDivision1(request.POST,request.FILES, instance=profile)
            p_form = AddDivisionForm(request.POST,request.FILES,instance=profile)
            p_form.user_id=request.user.id

            #print(p_form.user_id)
            if p_form.is_valid() and u_form.is_valid():
                p_form.save()
                u_form.save()
                messages.success(request,f'Your Account has been Updated11111')
                return redirect('index')
            print('diri')

        else:
        
            u_form = UserUpdateForm(request.POST,instance=request.user)
            fish = AddDivisionww.objects.get(user_id=request.user)  
            p_form = AddDivisionForm(request.POST,request.FILES,instance=fish)
     
    
            if p_form.is_valid() and u_form.is_valid():
                p_form.save()
                u_form.save()
                messages.success(request,f'Your Account has been Updated')
                return redirect('displayletter')
           
    else:
        
        if not AddDivisionww.objects.filter(user_id=request.user.id):
            u_form = UserUpdateForm(instance=request.user)

            p_form = AddDivisionForm(instance=request.user)
          
        else:
            u_form = UserUpdateForm(instance=request.user)

            fish = AddDivisionww.objects.get(user_id=request.user)       
            p_form = AddDivisionForm(instance=fish)
         
            
            
    context= {
        'u_form':u_form,
        'p_form':p_form,
    }

    return render(request,'adddivision1.html',context)



def letteractionarda(request,id):
    submitted = False
  
    if request.method == 'POST':

        if not Letter.objects.filter(id=id):
            print('test')
        else:
                fish = Letter.objects.get(id=id)
                reapply_form = LetterActionARDA(request.POST,request.FILES,instance=fish)
                if reapply_form.is_valid():
                     reapply_form.save()
                     if request.user != fish.user:
                        SampleNotification.objects.create(user=fish.user, message=f"Your letter '{fish.letter_desc}' has been edited by {request.user.username}",bjmptrans_no=fish.bjmptrans_no)
                     # Notify the original author via WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                        f"user_{fish.user}",
                        {
                            'type': 'send_notification',
                            'notification': f"Your letter '{fish.letter_desc}' has been updated by {request.user.username}"
                        }
                     )

                     messages.success(request,f'Successfully Approved Letter')
                     return redirect('displayletterRCDS')
    else:
            ids = Letter.objects.get(id=id)       
            reapply_form = LetterActionARDA(instance=ids)
     
    ids = Letter.objects.get(id=id)

    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'letteraction.html',context)


def letteractionardo(request,id):
    submitted = False
  
    if request.method == 'POST':

        if not Letter.objects.filter(id=id):
            print('test')
        else:
                fish = Letter.objects.get(id=id)
                reapply_form = LetterActionARDO(request.POST,request.FILES,instance=fish)
                if reapply_form.is_valid():
                     reapply_form.save()
                     if request.user != fish.user:
                        SampleNotification.objects.create(user=fish.user, message=f"Your letter '{fish.letter_desc}' has been edited by {request.user.username}",bjmptrans_no=fish.bjmptrans_no)
                     # Notify the original author via WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                        f"user_{fish.user}",
                        {
                            'type': 'send_notification',
                            'notification': f"Your letter '{fish.letter_desc}' has been updated by {request.user.username}"
                        }
                     )

                     messages.success(request,f'Successfully Approved Letter')
                     return redirect('displayletterRCDS')
    else:
            ids = Letter.objects.get(id=id)       
            reapply_form = LetterActionARDO(instance=ids)
     
    ids = Letter.objects.get(id=id)

    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'letteraction.html',context)

def letteractionrd(request,id):
    submitted = False
  
    if request.method == 'POST':

        if not Letter.objects.filter(id=id):
            print('test')
        else:
                fish = Letter.objects.get(id=id)
                reapply_form = LetterActionRD(request.POST,request.FILES,instance=fish)
                if reapply_form.is_valid():
                     reapply_form.save()


                     if request.user != fish.user:
                        SampleNotification.objects.create(user=fish.user, message=f"Your letter '{fish.letter_desc}' has been edited by {request.user.username}",bjmptrans_no=fish.bjmptrans_no)
                     # Notify the original author via WebSocket
                     channel_layer = get_channel_layer()
                     async_to_sync(channel_layer.group_send)(
                        f"user_{fish.user}",
                        {
                            'type': 'send_notification',
                            'notification': f"Your letter '{fish.letter_desc}' has been updated by {request.user.username}"
                        }
                     )
                     messages.success(request,f'Successfully Approved Letter')
                     return redirect('displayletterRCDS')
    else:
            ids = Letter.objects.get(id=id)       
            reapply_form = LetterActionRD(instance=ids)
     
    ids = Letter.objects.get(id=id)

    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'letteraction.html',context)


def msgcenteraction(request,id):
    submitted = False
  
    if request.method == 'POST':

        if not Letter.objects.filter(id=id):
            print('test')
        else:
                fish = Letter.objects.get(id=id)
                reapply_form = LetterActionmsgcenter(request.POST,request.FILES,instance=fish)
                if reapply_form.is_valid():
                     #actionrequest=Letter()
                     #actionrequest.action_request=request.POST.get('actionrequest')
                     #print(actionrequest.action_request)
                     reapply_form.save()


                     if request.user != fish.user:
                        SampleNotification.objects.create(user=fish.user, message=f"Your letter '{fish.letter_desc}' has been edited by {request.user.username}",bjmptrans_no=fish.bjmptrans_no)
                     # Notify the original author via WebSocket
                     channel_layer = get_channel_layer()
                     async_to_sync(channel_layer.group_send)(
                        f"user_{fish.user}",
                        {
                            'type': 'send_notification',
                            'notification': f"Your letter '{fish.letter_desc}' has been updated by {request.user.username}"
                        }
                     )
                     messages.success(request,f'Letter Dispatch')
                     return redirect('displaymsgcenter')
    else:
            ids = Letter.objects.get(id=id)       
            reapply_form = LetterActionmsgcenter(instance=ids)
     
    ids = Letter.objects.get(id=id)

    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'msgcenteraction.html',context)



def letteraction(request,id):
    submitted = False
  
    if request.method == 'POST':


        #ids = AddID.objects.get(id=id)
        if not Letter.objects.filter(id=id):
            print('ok')


        else:
                fish = Letter.objects.get(id=id)
               
                reapply_form = LetterAction(request.POST,request.FILES,instance=fish)
              
                if reapply_form.is_valid():
                     reapply_form.save()

                     if request.user != fish.user:
                        SampleNotification.objects.create(user=fish.user, message=f"Your letter '{fish.letter_desc}' has been edited by {request.user.username}",bjmptrans_no=fish.bjmptrans_no)
                     # Notify the original author via WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                        f"user_{fish.user}",
                        {
                            'type': 'send_notification',
                            'notification': f"Your letter '{fish.letter_desc}' has been updated by {request.user.username}"
                        }
                     )



           
                     messages.success(request,f'Successfully Approved Letter')
                     return redirect('displayletterRCDS')
    else:
            ids = Letter.objects.get(id=id)       
            reapply_form = LetterAction(instance=ids)

           
    ids = Letter.objects.get(id=id)

    context= {
        'reapply_form':reapply_form
        
        
    }

    return render(request,'letteraction.html',context)



@login_required
def notifications(request):
    user_notifications = SampleNotification.objects.filter(user=request.user, is_read=False)

    result = []
    for item in user_notifications:
        letter = Letter.objects.filter(bjmptrans_no=item.bjmptrans_no)
        for letter in letter:
            result.append({
                'user':item.user,
                'letter_desc':letter.letter_desc,
                'message':item.message,
                'created_at':item.created_at,
                'id':letter.bjmptrans_no,
                'id2':item.id
                })
    result={'result':result}   
    return render(request,"notifications.html",result)


def notification_count_api(request):
    user_id = request.user
    if user_id:
        contact = 0;
        count = SampleNotification.objects.filter(user=user_id, is_read=False).count()
        print(count)
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})




