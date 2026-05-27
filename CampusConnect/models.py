from django.db import models


class Student(models.Model):

    ROLE_CHOICES = (
        ('USER', 'User'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
    )

    full_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    username = models.CharField(max_length=50, unique=True)

    password = models.CharField(max_length=100)
    points = models.IntegerField(default=0)


    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='USER'
    )

    def __str__(self):
        return self.username


class Post(models.Model):
    # Fixed Category Choices as per your project flow
    CATEGORY_CHOICES = [
        ('Notes', 'Notes Requirement'),
        ('Coding', 'Coding Doubt'),
        ('Assignment', 'Assignment Help'),
        ('Updates', 'Classroom Update'),
        ('Campus Queries', 'Campus Query / Enquiry'),
    ]
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Open'),
            ('IN_PROGRESS', 'In Progress'),
            ('RESOLVED', 'Resolved'),
        ],
    default='OPEN'
    )

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='student_posts')
    
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    
    # Auto timestamp generation fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - By {self.student}"


class ChatRoom(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    requester = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='requester_chats')
    helper = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='helper_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat - {self.post.title}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:20]}"


class HelpRequest(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    helper = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.helper.username} -> {self.post.title}"