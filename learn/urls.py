from django.conf.urls import patterns, url
from learn import views
from django.conf import settings

from learn.views import QuizListView, CategoriesListView,\
    ViewQuizListByCourse, QuizUserProgressView, QuizMarkingList,\
    QuizMarkingDetail, QuizDetailView, QuizTake

urlpatterns = patterns('',

#      url(r'^$', 
#			views.index, 
#			name='index'),

  	   url(r'^register/$',
			views.register, 
			name='register'),

 	   url(r'^login/$', 
			views.user_login, 
			name='login'),

	   url(r'^restricted/', 
			views.restricted, 
			name='restricted'),

       url(r'^logout/$', 
			views.user_logout, 
			name='logout'),

	   url(regex=r'^$',
		   view=QuizListView.as_view(),
		   name='quiz_index'),

	   url(regex=r'^course/$',
		   view=CategoriesListView.as_view(),
		   name='quiz_course_list_all'),

	   url(regex=r'^course/(?P<course_name>[\w.-]+)/$',
		   view=ViewQuizListByCourse.as_view(),
		   name='quiz_course_list_matching'),

	   url(regex=r'^progress/$',
		   view=QuizUserProgressView.as_view(),
		   name='quiz_progress'),

	   url(regex=r'^marking/$',
		   view=QuizMarkingList.as_view(),
		   name='quiz_marking'),

	   url(regex=r'^marking/(?P<pk>[\d.]+)/$',
		   view=QuizMarkingDetail.as_view(),
		   name='quiz_marking_detail'),

	   #  passes variable 'quiz_name' to quiz_take view
	   url(regex=r'^(?P<slug>[\w-]+)/$',
		   view=QuizDetailView.as_view(),
		   name='quiz_start_page'),

	   url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
		   view=QuizTake.as_view(),
		   name='quiz_question'),

)
