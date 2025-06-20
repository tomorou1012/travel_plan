from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from . import models, forms
from .models import Notification, Post, Member
from .forms import PostForm, get_day_formset, get_schedule_formset
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class MemberLoginView(LoginView):
    template_name = 'travel_plan_app_HTML/member_login.html'

@login_required
def MemberLogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('member_login'))

class HomeView(LoginRequiredMixin, ListView):
    model = models.Post
    template_name = 'travel_plan_app_HTML/home.html'
    context_object_name = 'post_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        context['prefectures'] = models.Prefecture.objects.all
        return context 

    def get_queryset(self,**kwargs):
        queryset = super().get_queryset(**kwargs)
        prefecture_id = self.request.GET.get('prefecture')
        if prefecture_id:
            queryset = queryset.filter(prefecture_id=prefecture_id)

        query = self.request.GET.get('query')
        if query:
            queryset = queryset.filter(
                Q(place__icontains=query) |
                Q(prefecture__name__icontains=query) |
                Q(member__username__icontains=query)
            )
        return queryset 



class MemberRegistView(CreateView):
    model = models.Member
    form_class = forms.MemberForm
    template_name = 'travel_plan_app_HTML/member_regist.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        member = form.save(commit=False)
        member.set_password(form.cleaned_data['password1'])
        member.save()
        self.object = member
        login(self.request, member)
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    


class MemberUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Member
    form_class = forms.MemberUpdateForm
    template_name = 'travel_plan_app_HTML/member_regist.html'
    def get_success_url(self):
        return reverse('member_detail',  kwargs={'pk':self.object.pk})
    
    def form_valid(self, form):
        member = form.save(commit=False)

        if form.cleaned_data.get('password1'):
            member.set_password(form.cleaned_data['password1'])

        member.save()
        self.object = member

        if form.cleaned_data.get('password1'):
            login(self.request, member)

        return super().form_valid(form)    

    def form_invalid(self, form):
        logger.error('Form submission failed with errors: %s', form.errors)
        return self.render_to_response(self.get_context_data(form=form))
    


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = models.Member
    template_name = 'travel_plan_app_HTML/member_detail.html'
    context_object_name = 'member'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = models.Post.objects.filter(member=self.object)
        context['is_following'] = self.request.user in self.object.followers.all()
        return context
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = models.Post
    form_class = PostForm
    template_name = 'travel_plan_app_HTML/post_create.html'

    def get(self, request):
        form = PostForm()
        DayFormSet = get_day_formset(extra=1)
        ScheduleFormSet = get_schedule_formset(extra=1)
        day_formset = DayFormSet(prefix='days')
        schedule_formsets = {}

        for i, day_form in enumerate(day_formset.forms):
            prefix = f'schedules-day-{i}'
            day_instance = day_form.instance
            schedule_formsets[f'day-{i}'] = ScheduleFormSet(
                prefix=prefix,
                instance=day_instance
            )

        logger.info(f'スケジュールフォームセット:{schedule_formsets}')

        return render(request, self.template_name, {
            'form': form,
            'day_formset': day_formset,
            'schedule_formsets': schedule_formsets
        }) 

    def post(self, request):
        form = PostForm(request.POST)
        DayFormSet = get_day_formset(extra=1)
        ScheduleFormSet = get_schedule_formset(extra=1)

        day_formset = DayFormSet(request.POST, prefix='days')

        if form.is_valid() and day_formset.is_valid():
            member = self.request.user
            post = form.save(commit=False)
            post.member = member
            post.save()
            logger.info(f'Post saved: {post}, ID: {post.pk}')
            for i, day_form in enumerate(day_formset.forms):
                day = day_form.save(commit=False)
                day.post = post
                day.save()

                schedule_formset = ScheduleFormSet(request.POST, prefix=f'schedules-day-{i}', instance=day)
                if schedule_formset.is_valid():
                    schedule_formset.save()
                else:
                    print(f"ScheduleFormSet for day {i} has error: {schedule_formset.errors}")  
            
            return redirect('post_detail', pk=post.pk)
        
        else:
            schedule_formsets = {
                f'day-{i}': ScheduleFormSet(request.POST, prefix=f'schedules-day-{i}')
                for i in range(len(day_formset.forms))
            }
            return render(request, self.template_name, {
                'form': form,
                'day_formset':day_formset,
                'schedule_formsets': schedule_formsets
            })

class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'travel_plan_app_HTML/post_create.html'

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        DayFormSet = get_day_formset(extra=0)
        ScheduleFormSet = get_schedule_formset(extra=0)

        post_form = PostForm(instance=post)
        day_formset = DayFormSet(instance=post, prefix='days')
        schedule_formsets = {}
        
        for i, day_form in enumerate(day_formset.forms):
            prefix = f'schedules-day-{i}'
            day_instance = day_form.instance
            schedule_formset = ScheduleFormSet(instance=day_instance, prefix=prefix)
            schedule_formsets[f'day-{i}'] = schedule_formset

        context = {
            'form': post_form,
            'day_formset': day_formset,
            'schedule_formsets':schedule_formsets,
            'post': post 
        }

        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        DayFormSet = get_day_formset(extra=0)
        ScheduleFormSet = get_schedule_formset(extra=0)

        post_form = PostForm(request.POST, instance=post)
        day_formset = DayFormSet(request.POST, instance=post)
        schedule_formsets = {}
        is_valid = post_form.is_valid() and day_formset.is_valid()

        for i, day_form in enumerate(day_formset.forms):
            day_instance = day_form.instance
            prefix = f'schedules-day-{i}'
            schedule_formset = ScheduleFormSet(request.POST, instance=day_instance, prefix=prefix)
            schedule_formsets[f'day-{i}'] = schedule_formset

            if not schedule_formset.is_valid():
                is_valid = False

        if is_valid:
            post = post_form.save()
            days = day_formset.save(commit=False)

            for day in days:
                day.post = post
                day.save()

            for schedule_formset in schedule_formsets.values():
                schedule_formset.save()

            day_formset.save_m2m()

            return redirect('post_detail', pk = self.kwargs['pk'])
        
        else:
            context = {
                'form': post_form,
                'day_formset': day_formset,
                'schedule_formset': schedule_formset,
                'post': post
            }
            return render(request, self.template_name, context)

class PostDetailView(LoginRequiredMixin, DetailView):
    model = models.Post
    context_object_name = 'post_detail'
    template_name = 'travel_plan_app_HTML/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_liked = False
        post = self.get_object()
        if self.request.user.is_authenticated:
            is_liked = models.Like.objects.filter(member=self.request.user, post=post).exists()
        context['is_liked'] = is_liked
        context['comments'] =  post.comments.all()
        context['comment_form'] = forms.CommentForm()
        return context
     

class PostDeleteView(DeleteView):
    model = models.Post
    success_url = reverse_lazy('home')


class CommentCreateView(CreateView):
    model = models.Comment
    form_class = forms.CommentForm
    def form_valid(self, form):
        form.instance.member = self.request.user
        form.instance.post = get_object_or_404(models.Post, id=self.kwargs['pk'])
        form.save()

        if form.instance.post.member != self.request.user:
            models.Notification.objects.create(
                sender=self.request.user,
                recipient=form.instance.post.member,
                notification_type='comment',
                post=form.instance.post
            )

        return redirect('post_detail', pk=self.kwargs['pk'])    

class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        target_member = get_object_or_404(models.Member, pk=kwargs['pk'])
        current_member = request.user

        if target_member != current_member:
            if current_member in target_member.followers.all():
                target_member.followers.remove(current_member)
            else:
                target_member.followers.add(current_member)
                models.Notification.objects.create(
                    sender=current_member,
                    recipient=target_member,
                    notification_type='follow'
                )

        return redirect('member_detail', pk=target_member.pk)    

class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(models.Post, id=kwargs['pk'])
        like, created = models.Like.objects.get_or_create(member=request.user, post=post)

        if created:
            if post.member != request.user:
                models.Notification.objects.create(
                    sender=request.user,
                    recipient=post.member,
                    post=post,
                    notification_type='like'
                )
        else:
            like.delete()


        return redirect('post_detail', pk=post.id)
    
class NotificationListView(LoginRequiredMixin, ListView):
    model = models.Notification
    template_name = 'travel_plan_app_HTML/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return models.Notification.objects.filter(recipient=self.request.user).order_by('-created_at')
        
    def get(self, request, *args, **kwargs):
        notifications = self.get_queryset()
        unread_notifications = notifications.filter(is_read=False)
        unread_notifications.update(is_read=True)

        return super().get(request, *args, **kwargs) 

class PopularPostListView(LoginRequiredMixin, ListView):
    model = models.Post
    template_name = 'travel_plan_app_HTML/popular_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_posts'] = models.Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:10]
        return context
    
class LatestPostListView(LoginRequiredMixin, ListView):
    model = models.Post
    template_name = 'travel_plan_app_HTML/latest_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = models.Post.objects.order_by('-created_at')[:10]
        return context

class LikedPostListView(LoginRequiredMixin, ListView):
    model = models.Like
    template_name = 'travel_plan_app_HTML/liked_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        likes = models.Like.objects.filter(member=self.request.user)
        context['liked_posts'] = [like.post for like in likes]
        return context    















