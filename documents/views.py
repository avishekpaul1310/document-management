from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Document, Category
from .forms import DocumentForm, UserRegistrationForm, BatchUploadForm
from django.utils import timezone
from datetime import timedelta

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    selected_category = category
    
    documents = Document.objects.filter(
        Q(owner=request.user) | Q(is_private=False)
    )
    
    if query:
        documents = documents.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    if category:
        documents = documents.filter(category__name=category)
    
    categories = Category.objects.all()
    
    summary = {
        'total_documents': Document.objects.filter(owner=request.user).count(),
        'total_categories': Category.objects.filter(document__owner=request.user).distinct().count(),
        'recent_uploads': Document.objects.filter(
            owner=request.user,
            uploaded_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'private_documents': Document.objects.filter(owner=request.user, is_private=True).count()
    }
    
    context = {
        'documents': documents,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'summary': summary,
    }
    return render(request, 'documents/dashboard.html', context)

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentForm()
    
    context = {
        'form': form,
        'title': 'Upload Document'  # Add this for the template
    }
    return render(request, 'documents/document_upload.html', context)

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if document.is_private and document.owner != request.user:
        return HttpResponseForbidden()
    return render(request, 'documents/document_detail.html', {'document': document})

@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Only allow the owner to delete the document
    if document.owner != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'documents/document_delete.html', {'document': document})

def batch_upload(request):
    if request.method == 'POST':
        form = BatchUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            category = form.cleaned_data['category']
            is_private = form.cleaned_data['is_private']
            
            uploaded_count = 0
            for file in files:
                try:
                    Document.objects.create(
                        title=file.name,
                        description=f'Uploaded as part of batch upload on {timezone.now().strftime("%Y-%m-%d")}',
                        file=file,
                        category=category,
                        owner=request.user,
                        is_private=is_private
                    )
                    uploaded_count += 1
                except Exception as e:
                    messages.error(request, f'Error uploading {file.name}: {str(e)}')
            
            if uploaded_count > 0:
                messages.success(request, f'Successfully uploaded {uploaded_count} documents!')
            return redirect('dashboard')
    else:
        form = BatchUploadForm()
    
    return render(request, 'documents/batch_upload.html', {
        'form': form,
        'title': 'Batch Upload Documents'
    })