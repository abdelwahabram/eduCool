from django.db import models


def get_course_attachments_dir(instance, filename):
	
	"""
	Description: format the file system path to store the attachment

	Args: instance=> instance of the course model,
		filename=> the uploaded file name
	"""

	return "attachments/{instance.title}/%Y/%m/%d/{filename}"


class Course(models.Model):

    """
    Description: just as the title, a room that gathers students and tutors
    """
    
    tutor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='courses')

    title = models.TextField(max_length= 150, blank= False, default='')

    students = models.ManyToManyField('auth.User')


class Announcement(models.Model):

    """
    Description: what tutors post to the course students
    """

    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='announcements')
    
    title = models.TextField(max_length=150, blank = True, default='')
    
    content = models.TextField(max_length=1000, blank = False, default = '')
    
    time = models.DateTimeField(auto_now_add=True)
    
    attachment = models.FileField(upload_to=get_course_attachments_dir, null=True, blank=True)
    
    #NOTE: it defaults to the file system storage
    # would rather use a proper object storage sys in production


class Comment(models.Model):

    """
    Description: What students or tutors commented on an anouncement
    """

    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, related_name='comments')
    
    content = models.TextField(max_length=500, blank=False, default='')
    
    time = models.DateTimeField(auto_now_add=True)
