from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token}"


class AddID(models.Model):
	#user = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=250,null=True)
	last_name=models.CharField(max_length=250,null=True)
	midle_initial = models.CharField(max_length=250,null=False)
	id_pic = models.ImageField(null=True,blank=True,upload_to="images/picture")
	signature = models.ImageField(null=True,blank=True,upload_to="images/signature")
	contact_person = models.CharField(max_length=250, null=False)
	contact_person_no = models.CharField(max_length=250,null=False)
	address = models.TextField(null=False)
	sss_no = models.CharField(max_length=250,null=False)
	tin = models.CharField(max_length=250,null=False)
	#philhealth_no = models.CharField(max_length=250,null=False)
	employee_no = models.CharField(max_length=250,null=False)
	birth_date = models.DateField(null=True)
	disignation = models.CharField(max_length=250,null=True)
	id_code = models.CharField(max_length=250,null=False,default='',blank=True)
	contact_person_address = models.TextField(null=True)
	blood_type = models.CharField(max_length=250,null=True,blank=True)
	name_extension = models.CharField(max_length=250, null= False,default='',blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	id_status = {
		('Pending','Pending'),
		('For Edit','For Edit'),
		('Completed','Completed'),
	}
	status = models.CharField(max_length=150,choices=id_status,default='Pending')
	transaction_no=models.CharField(max_length=250,null=True)
	date_printed = models.DateField(null=True)
	remarks = models.TextField(null=True)

class Employee(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=250,null=True)
	last_name=models.CharField(max_length=250,null=True)
	midle_initial = models.CharField(max_length=250,null=True)
	id_pic = models.ImageField(null=True,blank=True,upload_to="images/picture")
	signature = models.FileField(null=True,blank=True,upload_to="images/signature")
	contact_person = models.CharField(max_length=250, null=True)
	contact_person_no = models.CharField(max_length=250,null=True)
	address = models.TextField(null=True)
	sss_no = models.CharField(max_length=250,null=True)
	tin = models.CharField(max_length=250,null=True)
	philhealth_no = models.CharField(max_length=250,null=True)
	employee_no = models.CharField(max_length=250,null=True)
	birth_date = models.DateField(null=True)
	disignation = models.CharField(max_length=250,null=True)
	id_code = models.CharField(max_length=250,null=False,default='',blank=True)
	contact_person_address = models.TextField(null=True)
	blood_type = models.CharField(max_length=250,null=True,blank=True)
	name_extension = models.CharField(max_length=250, null= False,default='',blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering=['disignation']

		

class ID(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='+')
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='+',null=True)
	
	id_status = {
		('Pending','Pending'),
		('For Edit','For Edit'),
		('Completed','Completed'),
	}
	status = models.CharField(max_length=150,choices=id_status,default='Pending')
	date_printed =models.DateField(null=True)
	remarks = models.CharField(max_length=250,null=True)
	transaction_no = models.CharField(max_length=250,null=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Forclaim(models.Model):
	user =  models.CharField(max_length=250,null=False)
	transaction_no = models.CharField(max_length=250,null=True)
	date_printed = models.DateField(null=True)


class ForclaimAdmin(models.Model):
	employee =  models.CharField(max_length=250,null=False)
	transaction_no = models.CharField(max_length=250,null=True)
	date_printed = models.DateField(null=True)


class Idcode(models.Model):
	user =models.ForeignKey(User, on_delete=models.CASCADE)
	department = models.CharField(max_length=250,null=False)
	id_code = models.CharField(max_length=250,null=False)

class DeptandDesignation(models.Model):
	fullname=models.CharField(max_length=250,null=True)
	designation=models.CharField(max_length=250,null=True)
	idcode=models.CharField(max_length=250,null=True)

class Idapplication(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	transaction_no=models.CharField(max_length=250,null=True)
	created_at = models.DateField(auto_now_add=True,null=True)

class DivisionOffice(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name=models.CharField(max_length=250,null=True)
	last_name=models.CharField(max_length=250,null=True)
	midle_initial = models.CharField(max_length=250,null=True)
	division_name = models.CharField(max_length=250,null=True)

class Letter(models.Model):
	user=models.CharField(max_length=250,null=False)
	letter_desc = models.CharField(max_length=250,null=True)
	sender = models.CharField(max_length=250,null=True)
	date_send = models.DateTimeField(auto_now_add=True)
	letter_status = {
		('Pending','Pending'),
		('Approved','Approved'),
		('Disapproved','Disapproved'),
		('On Leave','On Leave'),
		('Official Business','Official Business'),

		
	}
	dispatch_status = {
		('Pending','Pending'),
		('Dispatched','Dispatched'),
	}
	aprover_1= models.CharField(max_length=250, null= True,default='RCDS',blank=True)
	stat_1= models.CharField(max_length=150,choices=letter_status,default='Pending')#RCDS
	aprover_2= models.CharField(max_length=250, null= True,default='ARDA',blank=True)
	stat_2= models.CharField(max_length=150,choices=letter_status,default='Pending')#ARDA
	aprover_3= models.CharField(max_length=250, null= True,default='RD',blank=True)
	stat_3= models.CharField(max_length=150,choices=letter_status,default='Pending')#RD
	aprover_4= models.CharField(max_length=250, null= True,default='ARDO',blank=True)
	stat_4= models.CharField(max_length=150,choices=letter_status,default='Pending')#ARDO
	bjmptrans_no=models.CharField(max_length=250,null=True)
	#letter_pdf = models.FileField(null=True,upload_to="pdf/letters")
	#mega_file_id = models.CharField(max_length=255, blank=True, null=True)#for MEGA storage/render
	#letter_pdf = models.URLField(max_length=500, blank=True, null=True)#for MEGA storage/render
	letter_pdf = models.URLField(max_length=500, blank=True, null=True)
	action_request = models.CharField(max_length=250,null=True,blank=True)
	date_aprov_1 = models.DateTimeField(auto_now_add=True,null=True)#RD
	date_aprov_2 = models.DateTimeField(auto_now_add=True,null=True)#ARDA
	date_aprov_3 = models.DateTimeField(auto_now_add=True,null=True)#RCDS
	date_aprov_4 = models.DateTimeField(auto_now_add=True,null=True)#ARDO
	comment_rcds = models.TextField(max_length=250,null=True,blank=True)
	comment_arda = models.TextField(max_length=250,null=True,blank=True)
	comment_rd = models.TextField(max_length=250,null=True,blank=True)
	comment_ardo = models.TextField(max_length=250,null=True,blank=True)
	updated_date = models.DateTimeField(auto_now_add=True,null=True)
	dispatch= models.CharField(max_length=150,choices=dispatch_status,default='Pending')

	def __init__(self, *args, **kwargs):
		super(Letter, self).__init__(*args, **kwargs)
		self._stat_3 = self.stat_3
		self._stat_2 = self.stat_2
		self._stat_1 = self.stat_1
		self._stat_4 = self.stat_4
		self._letter_pdf = self.letter_pdf
		self._comment_rd = self.comment_rd
		self._comment_arda = self.comment_arda
		self._comment_ardo = self.comment_ardo
		self._comment_rcds = self.comment_rcds


	def save(self, *args, **kwargs):
		if not self._stat_3 == self.stat_3:
			self.date_aprov_1  = timezone.now()
		elif not self._stat_2 == self.stat_2:
			self.date_aprov_2  = timezone.now()
		elif not self._stat_1 == self.stat_1:
			self.date_aprov_3  = timezone.now()
		elif not self._stat_4 == self.stat_4:
			self.date_aprov_4  = timezone.now()
		elif not self._comment_ardo == self.comment_ardo:
			self.date_aprov_4  = timezone.now()
		elif not self._comment_arda == self.comment_arda:
			self.date_aprov_2  = timezone.now()
		elif not self._comment_rcds == self.comment_rcds:
			self.date_aprov_3  = timezone.now()
		elif not self._comment_rd == self.comment_rd:
			self.date_aprov_1  = timezone.now()
		elif not self._letter_pdf == self.letter_pdf:
			self.updated_date  = timezone.now()
			#print(stat_3)
			print('pareha')
		else:
			print(self._stat_3)
			print('di pareho')
		super(Letter,self).save(*args, **kwargs)
		
	def __str__(self):
		return self.message

"""def save(self, *args, **kwargs):
    if self.stat_2 and self.date_aprov_1 is None:
        self.date_aprov_1 = timezone.now()
    elif not self.stat_2 and self.date_aprov_1 is not None:
         self.stat_2 = date_aprov_1
    super(Model, self).save(*args, **kwargs)"""


class AddDivisionww(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    division_name = models.CharField(max_length=50, null=True)
    rank = models.CharField(max_length=50, null=True)
    signature = models.FileField(null=True,blank=True,upload_to="images/signature")


class SampleLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    samplecontent = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

class SampleNotification(models.Model):
    user=models.CharField(max_length=250,null=False)
    bjmptrans_no=models.CharField(max_length=250,null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)








	
	

