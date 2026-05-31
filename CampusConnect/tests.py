from django.test import TestCase, Client
from django.urls import reverse

from .models import (
    Student,
    Post,
    ChatRoom,
    Message,
    HelpRequest
)


class BaseTestCase(TestCase):

    def setUp(self):

        self.client = Client()

        self.user = Student.objects.create(
            full_name="Normal User",
            email="user@test.com",
            username="user1",
            password="123",
            role="USER"
        )

        self.helper = Student.objects.create(
            full_name="Helper User",
            email="helper@test.com",
            username="helper1",
            password="123",
            role="USER"
        )

        self.staff = Student.objects.create(
            full_name="Staff User",
            email="staff@test.com",
            username="staff1",
            password="123",
            role="STAFF"
        )

        self.admin = Student.objects.create(
            full_name="Admin User",
            email="admin@test.com",
            username="admin1",
            password="123",
            role="ADMIN"
        )

        self.post = Post.objects.create(
            student=self.user,
            title="Need Python Notes",
            category="Notes",
            description="Need semester notes"
        )


# MODEL TESTS

class StudentModelTest(BaseTestCase):

    def test_student_creation(self):
        self.assertEqual(self.user.username, "user1")

    def test_student_default_points(self):
        self.assertEqual(self.user.points, 0)

    def test_student_str(self):
        self.assertEqual(str(self.user), "user1")


class PostModelTest(BaseTestCase):

    def test_post_creation(self):
        self.assertEqual(self.post.title, "Need Python Notes")

    def test_post_default_status(self):
        self.assertEqual(self.post.status, "OPEN")


class HelpRequestModelTest(BaseTestCase):

    def test_help_request_creation(self):

        help_req = HelpRequest.objects.create(
            post=self.post,
            helper=self.helper
        )

        self.assertFalse(help_req.is_accepted)


class ChatRoomModelTest(BaseTestCase):

    def test_chat_room_creation(self):

        room = ChatRoom.objects.create(
            post=self.post,
            requester=self.user,
            helper=self.helper
        )

        self.assertEqual(room.post, self.post)


class MessageModelTest(BaseTestCase):

    def test_message_creation(self):

        room = ChatRoom.objects.create(
            post=self.post,
            requester=self.user,
            helper=self.helper
        )

        msg = Message.objects.create(
            room=room,
            sender=self.user,
            message="Hello"
        )

        self.assertEqual(msg.message, "Hello")


# AUTHENTICATION TESTS

class AuthenticationTests(BaseTestCase):

    def test_login_user(self):

        response = self.client.post(
            reverse("login"),
            {
                "username": "user1",
                "password": "123",
                "role": "USER"
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):

        response = self.client.post(
            reverse("login"),
            {
                "username": "wrong",
                "password": "wrong",
                "role": "USER"
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_signup(self):

        response = self.client.post(
            reverse("signup"),
            {
                "full_name": "New User",
                "email": "new@test.com",
                "username": "newuser",
                "password": "123",
                "role": "USER"
            }
        )

        self.assertTrue(
            Student.objects.filter(username="newuser").exists()
        )

    def test_logout(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)



# URL TESTS

class URLTests(BaseTestCase):

    def test_home_url(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_signup_url(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_about_url(self):
        response = self.client.get(reverse("about_platform"))
        self.assertEqual(response.status_code, 200)


# DASHBOARD TESTS

class DashboardTests(BaseTestCase):

    def login_user(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

    def test_dashboard_requires_login(self):

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_access(self):

        self.login_user()

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)



# ROLE TESTS

class RoleAccessTests(BaseTestCase):

    def test_staff_dashboard_staff(self):

        session = self.client.session
        session["student_id"] = self.staff.id
        session.save()

        response = self.client.get(
            reverse("staff_dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_admin(self):

        session = self.client.session
        session["student_id"] = self.admin.id
        session.save()

        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_denied_for_user(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        response = self.client.get(
            reverse("admin_dashboard")
        )

        self.assertEqual(response.status_code, 302)



# HELP REQUEST TESTS

class HelpRequestTests(BaseTestCase):

    def login_helper(self):

        session = self.client.session
        session["student_id"] = self.helper.id
        session.save()

    def test_send_help_request(self):

        self.login_helper()

        self.client.get(
            reverse(
                "send_help_request",
                args=[self.post.id]
            )
        )

        self.assertTrue(
            HelpRequest.objects.filter(
                post=self.post,
                helper=self.helper
            ).exists()
        )

    def test_cannot_duplicate_help_request(self):

        HelpRequest.objects.create(
            post=self.post,
            helper=self.helper
        )

        self.login_helper()

        self.client.get(
            reverse(
                "send_help_request",
                args=[self.post.id]
            )
        )

        count = HelpRequest.objects.filter(
            post=self.post,
            helper=self.helper
        ).count()

        self.assertEqual(count, 1)



# CHAT TESTS

class ChatTests(BaseTestCase):

    def setUp(self):

        super().setUp()

        self.room = ChatRoom.objects.create(
            post=self.post,
            requester=self.user,
            helper=self.helper
        )

    def test_chat_room_page(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        response = self.client.get(
            reverse("chatroom", args=[self.room.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_send_message(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        self.client.post(
            reverse("chatroom", args=[self.room.id]),
            {
                "message": "Hello helper"
            }
        )

        self.assertTrue(
            Message.objects.filter(
                message="Hello helper"
            ).exists()
        )

    def test_my_chats_page(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        response = self.client.get(
            reverse("my_chats")
        )

        self.assertEqual(response.status_code, 200)



# POST MANAGEMENT TESTS

class PostTests(BaseTestCase):

    def test_create_post(self):

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        self.client.post(
            reverse("post_need"),
            {
                "title": "Assignment Help",
                "category": "Assignment",
                "description": "Need help"
            }
        )

        self.assertTrue(
            Post.objects.filter(
                title="Assignment Help"
            ).exists()
        )

    def test_mark_resolved(self):

        help_req = HelpRequest.objects.create(
            post=self.post,
            helper=self.helper,
            is_accepted=True
        )

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        self.client.get(
            reverse(
                "mark_resolved",
                args=[self.post.id]
            )
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.status,
            "RESOLVED"
        )

    def test_reopen_post(self):

        self.post.status = "IN_PROGRESS"
        self.post.save()

        session = self.client.session
        session["student_id"] = self.user.id
        session.save()

        self.client.get(
            reverse(
                "reopen_post",
                args=[self.post.id]
            )
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.status,
            "OPEN"
        )
