from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from .models import UserProfile, Post, Comment
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponseBadRequest

# Create your views here.

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Get the date of birth from the form, or use a default value if not provided
        dob = request.POST.get('dob', '2000-01-01')

        if User.objects.filter(username=username).exists():
            error_message = "Username is already in use. Please choose a different username."
            return render(request, 'register.html', {'error_message': error_message})

        if password == confirm_password:
            # Create a new user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Convert the dob string to a DateField format
            from datetime import datetime
            dob = datetime.strptime(dob, "%Y-%m-%d").date()

            # Create a user profile with the provided or default date of birth
            user_profile = UserProfile(user=user, phone_number=phone_number, name="", address="", age=0, dob=dob)
            user_profile.save()

            # Log in the user
            login(request, user)
            
            # Check if the user has a profile, and redirect accordingly
            if hasattr(user, 'userprofile'):
                return redirect('user_profile')  # Existing user with a profile
            else:
                return redirect('home')  # New user without a profile
        else:
            error_message = "Passwords do not match. Please ensure both passwords are the same."
            return render(request, 'register.html', {'error_message': error_message})
    
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                # Attempt to retrieve the user's profile
                profile = UserProfile.objects.get(user=user)
                # User has a profile, redirect to the home page
                return redirect('home')
            except UserProfile.DoesNotExist:
                # User doesn't have a profile, redirect to the user's profile page
                return redirect('user_profile')
        else:
            if not username:
                messages.error(request, 'Please enter your username.')
            elif not password:
                messages.error(request, 'Please enter your password.')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    
    
    return render(request, 'login.html')

    
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the session to prevent logout
            messages.success(request, 'Your password was successfully updated!')
            print("Password change successful.")  # Debugging print statement
            return redirect('user_login')  # Redirect to the login page after changing password
        else:
            # Iterate over form errors and add them to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            print("Form errors:", form.errors)  # Debugging print statement
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

# home_page 
# __________________________________________________________________________________________________


@login_required
def home(request):
    recent_posts = Post.objects.order_by('-timestamp')[:10]
    return render(request, 'home.html', {'recent_posts': recent_posts})


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        text = request.POST['text']
        post = Post.objects.get(pk=post_id)
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        data = {
            'text': comment.text,
            'username': comment.user.username,
        }
        return JsonResponse(data)
    return redirect('home')

@login_required
def edit_comment(request, comment_id):
    # Retrieve the comment based on the comment_id
    comment = Comment.objects.get(pk=comment_id)

    if request.method == 'POST':
        # Handle the comment editing logic here
        new_text = request.POST.get('new_text')  # Get the edited comment text from the form
        comment.text = new_text  # Update the comment text
        comment.save()  # Save the updated comment

        # Redirect to the home page or wherever appropriate
        return redirect('home')  # Change 'home' to the name of your home page URL pattern

    # If it's not a POST request, just render the edit comment form
    return render(request, 'edit_comment.html', {'comment': comment})


@login_required
def delete_comment(request, comment_id):
    # Retrieve the comment based on the comment_id
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if the user has permission to delete the comment (e.g., comment.user == request.user)
    if comment.user == request.user:
        comment.delete()

    # Redirect to the home page or wherever appropriate
    return redirect('home')  # Change 'home' to the name of your home page URL pattern



# post_page 
# __________________________________________________________________________________________________


@login_required
def post_page(request):
    # Retrieve the user's posts
    user = request.user
    user_posts = Post.objects.filter(user=user).order_by('-timestamp')  # Assuming you have a 'timestamp' field
    
    if request.method == 'POST':
        # Handle post creation and editing here
        # Example: Create a new post
        post_name = request.POST['post_name']
        post_description = request.POST['post_description']
        category = request.POST['category']
        post_image = request.FILES.get('post_image')

        new_post = Post(user=user, post_name=post_name, post_description=post_description, category=category, post_image=post_image)
        new_post.save()
    
    return render(request, 'post_page.html', {'user_posts': user_posts})



@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)

    if request.method == 'POST':
        post_name = request.POST['post_name']
        post_description = request.POST['post_description']
        category = request.POST['category']
        post_image = request.FILES.get('post_image')  # Get the uploaded image

        if post.user == request.user:  # Check if the user is the owner of the post
            post.post_name = post_name
            post.post_description = post_description
            post.category = category

            if post_image:  # If a new image is uploaded, update it
                post.post_image = post_image

            post.save()
            return redirect('post_page')

    return render(request, 'edit_post.html', {'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)

    if request.method == 'POST':
        # Handle the post deletion logic here
        post.delete()
        return redirect('post_page')

    return render(request, 'delete_post.html', {'post': post})

@login_required
def upload_post(request):
    if request.method == 'POST':
        # Handle post upload logic here
        # Example: Create a new post and save it to the database
        post_name = request.POST['post_name']
        post_description = request.POST['post_description']
        category = request.POST['category']
        post_image = request.FILES.get('post_image')
        
        # Example: Create a new post associated with the current user
        post = Post(user=request.user, post_name=post_name, post_description=post_description, category=category, post_image=post_image)
        post.save()
        
        messages.success(request, 'Post uploaded successfully.')


# profile_page 
# __________________________________________________________________________________________________

@login_required
def user_profile(request):
    user = request.user

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If the user doesn't have a profile, create one
        profile = UserProfile(user=user)

    if request.method == 'POST':
        # Handle profile update logic here
        profile.name = request.POST['name']
        profile.address = request.POST['address']
        profile.age = request.POST['age']
        profile.dob = request.POST['dob']

        # Check if a new profile picture was uploaded
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        try:
            # Attempt to save the profile
            profile.full_clean()
            profile.save()

            # Redirect to home page after updating the profile
            return redirect('home')
        except ValidationError as e:
            # Handle validation errors and display error messages
            pass  # Replace with your error handling logic

    context = {
        'profile': profile,
    }

    return render(request, 'profile.html', context)


def remove_profile_pic(request):
    # Remove the user's profile picture logic goes here
    # For example, you can set the user's profile_pic field to None
    request.user.userprofile.profile_pic = None
    request.user.userprofile.save()
    
    # Redirect back to the user's profile page
    return redirect('user_profile')

# logout_page 
# __________________________________________________________________________________________________

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('user_login')


# admin_page 
# __________________________________________________________________________________________________

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')  # Redirect to admin dashboard
    return render(request, 'adminlogin.html')

@login_required
def admin_dashboard(request):
    # Filter out the admin user (superuser)
    users = User.objects.exclude(is_superuser=True)

    return render(request, 'admin_dashboard.html', {'users': users})


def activate_user(request, user_id):
    try:
        # Retrieve the user based on the user_id parameter
        user = User.objects.get(id=user_id)

        # Activate the user
        user.is_active = True
        user.save()

        # Add a success message
        messages.success(request, f'User {user.username} has been activated.')

        return redirect('admin_dashboard')  # Redirect to the admin dashboard or any other appropriate URL
    except User.DoesNotExist:
        # Handle the case where the user does not exist
        messages.error(request, 'User not found.')
        return redirect('admin_dashboard')  # Redirect to the admin dashboard or any other appropriate URL

def deactivate_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('admin_dashboard')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('admin_dashboard')

