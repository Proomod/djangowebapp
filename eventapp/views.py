from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from braces.views import SelectRelatedMixin
from eventapp import models
from django.http import HttpResponseRedirect, HttpResponse
from .forms import ImageForm, PostForm
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.templatetags.static import static
from django.views import generic

# Create your views here.
def index(request):
    path = settings.MEDIA_ROOT
    img_list = os.listdir(path + "/images")
    context = {"images": img_list}
    return render(request, "gallery.html", context)


@login_required
def post(request):

    ImageFormSet = modelformset_factory(models.Images, form=ImageForm, extra=10)
    #'extra' means the number of photos that you can upload   ^
    if request.method == "POST":
        postForm = PostForm(request.POST)
        formset = ImageFormSet(
            request.POST, request.FILES, queryset=models.Images.objects.none()
        )

        if postForm.is_valid() and formset.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()
            id = str(post_form.id)
            for form in formset.cleaned_data:
                # this helps to not crash if the user
                # do not upload all the photos
                if form:
                    image = form["image"]
                    photo = models.Images(post=post_form, image=image)
                    photo.save()
            messages.success(request, "Yeeew, check it out on the home page!")
            return HttpResponseRedirect("/eventapp/add_members/" + id)
        else:
            print(postForm.errors, formset.errors)
    else:
        postForm = PostForm()
        formset = ImageFormSet(queryset=models.Images.objects.none())
    return render(
        request, "gallery/eventbase.html", {"postForm": postForm, "formset": formset}
    )


# @login_required
# def memberpost(request):
#     if request.method == "POST":
#         member = Members
#         firstname = request.POST["first_name"]
#         lastname = request.POST["last_name"]
#         position = request.POST["position"]

#         if firstname:
#             member.first_name = firstname
#         if lastname:
#             member.last_name = lastname
#         if position:
#             member.position = position

#         image = request.FILES("photo")
#         if image:
#             member.photo = image
#         fss = FileSystemStorage()
#         fss.save("members/" + image.name, image)
#         return redirect()


def showGallery(request):
    posts = models.Postevent.objects.filter().order_by("-created_date")
    for i in posts:
        i.images = models.Images.objects.filter(post=i)[:2]
    return render(request, "footer.html", {"posts": posts})


def event_detail(request, id):
    eventdetail = models.Postevent.objects.get(id=id)
    eventdetail.images = models.Images.objects.filter(post=eventdetail)

    return render(request, "event_detail.html", {"event": eventdetail})


def upcoming_events(request):
    events = models.Postevent.objects.filter(completed=False).order_by("-created_date")[
        :10
    ]
    for event in events:
        event.images = models.Images.objects.filter(post=event)[:1]
        try:
            memberobjs = models.Members.objects.filter(post=event)
            for memberobj in memberobjs:
                event.person = models.People.objects.get(id=memberobj.person.id)
        except:
            pass
            # return HttpResponse("not found")
    return render(request, "upcoming_events.html", {"events": events})


def completed_events(request):
    events = models.Postevent.objects.filter(completed=True).order_by("-created_date")[
        :10
    ]
    for i in events:
        i.reduceddescription = i.description[:100]
        i.images = models.Images.objects.filter(post=i)
    return render(request, "completed_events.html", {"events": events})


# class PosteventDeleteview(LoginRequiredMixin, generic.DeleteView):
#     model = models.Postevent

#     success_url = reverse_lazy("/")
#     template_name = "gallery/deleted.html"

#     # def get_queryset(self):
#     #     queryset = super().get_queryset()
#     #     return queryset.filter(id=self.request.id)

#     def delete(self, *args, **kwargs):
#         messages.success(self.request, "Event Deleted")
#         return super().delete(*args, **kwargs)


@login_required
def deletepost(request, id):
    deleted = models.Postevent.objects.get(id=id)
    deleted.delete()
    return render(request, "gallery/deleted.html")


@login_required
def add_members(request, id):
    people = models.People.objects.all()
    try:
        post = models.Postevent.objects.get(id=id)
        for person in people:
            try:
                member = models.Members.objects.filter(post=post).get(person=person)
                if member:
                    person.truth = True
            except:
                person.truth = False
    except:
        return redirect("/")
    return render(request, "gallery/add_members.html", {"people": people, "pid": id})


@login_required
def add_member(request, pid, mid):
    if request.method == "POST":
        try:
            post = models.Postevent.objects.get(id=pid)
            try:
                person = models.People.objects.get(id=mid)
                try:

                    member = models.Members.objects.filter(person=person).get(post=post)
                    if member:
                        member.delete()
                        truth = "false"
                        return JsonResponse({"data": truth})
                except:

                    nmember = models.Members()

                    nmember.person = person
                    nmember.post = post
                    nmember.save()

                    return JsonResponse({"data": "true"})
            except:
                return redirect("/")
        except:
            return redirect("/")

