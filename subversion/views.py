#coding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.
from .models import Subversion
import forms
import models
import django.utils.timezone as timezone
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.decorators import permission_required
import paramiko
from django.contrib import messages
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

people=[]

def SSH(svnname,filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(hostname=host, port=22, username=username, password=password)
    ssh.connect(hostname='192.168.100.249', port=22, username="root", password="t3nfltc2d6")
    print "start command"
    #command = 'cd /data/svn/ && sh /data/svn/svn_create.sh %s /var/tmp/svnupload/%s' %(svnname,filename)
    command = 'cd /data/svn/ && sh /data/svn/svn_create.sh %s /var/tmp/svnupload/%s' %(svnname,filename)
    print command
    stdin, stdout, stderr = ssh.exec_command(str(command))
    print "over"
    ssh.close()



@login_required()
def svnlist(request):
	svn_list = Subversion.objects.all()
	return render(request, 'svn/svn_list.html',context ={ 'svn_list': svn_list})

@login_required()
def svn_add(request):
    if request.method == "POST":
            print "bbb"
            form = forms.SvnInfo(request.POST,request.FILES)
            #message = "请检查填写的内容！"
            if form.is_valid():

                svn_enname = form.cleaned_data['svn_enname']
                svn_company = form.cleaned_data['svn_company']
                svn_zhname = form.cleaned_data['svn_zhname']
                svn_url = form.cleaned_data['svn_url']
                print "start"
                print svn_enname,svn_company,svn_url,svn_zhname
		
		try:
                    aaa=Subversion.objects.get(svn_enname=svn_enname)
                    if aaa:
                        print "svn仓库名已被使用"
                        return HttpResponse("svn仓库名已经使用")
                except:

              		try:
                		File = request.FILES.get("myfile", None)
                		print File.name
				filename=str(File.name)
				print filename
				print type(filename)
                		if File:
                			with open("./svnupload/%s" % File.name, 'wb+') as f:
                            			# 分块写入文件
                            			for chunk in File.chunks():
                                			f.write(chunk)
                		else:
                        		print "no file"
				cmd = "scp ./svnupload/%s 192.168.100.249:/var/tmp/svnupload" %(File.name)
				os.system(cmd)
                		print svn_enname, svn_company, svn_url, svn_zhname
				SSH(svnname=svn_enname,filename=File.name)
                   		new = models.Subversion.objects.create()
                   		new.svn_enname = svn_enname
                   		new.svn_company = svn_company
                   		new.svn_zhname = svn_zhname
                   		new.svn_url = svn_url
                   		new.save()
				
				cmd1 = "scp 192.168.100.249:/home/newpeople.txt /opt/svninfo/"
				os.system(cmd1)
					
				f = open('/opt/svninfo/newpeople.txt', 'r')           #如改变文件位置需要修改
				people = f.read()
				people="".join(people)
				people=people.strip()
				people=people.split(",")
				people=",".join(people)

				f.close()
				
				messages.success(request,people)
				print people
                		return redirect('svnlist.html')
    			#	return render(request, 'svn/svn_list.html', context={'people': people})
					
                	except:
                    		message = ""
                    		return redirect('svn_add.html')
            		else:
                		print "aaaa"
                		print form.errors

    form = forms.SvnInfo()
    return render(request, 'svn/svn_add.html', {'form': form})

def svn_delete(request,pk):
    svn=Subversion.objects.get(pk=pk)
    svn.delete()
    return redirect('/svnlist')
