from django.shortcuts import render, redirect, get_object_or_404

def support(request):
    message = "Support page is working!"
    
    context = {
        'message': message,
    }
    return render(request, "support.html", context)