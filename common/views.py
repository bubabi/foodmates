from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from common import decisiontree, choices
from common.resources import ConditionResource
from django.views import generic, View
from common.forms import VoteForm, ConditionForm
from common.models import Place, Vote, Profile, Condition
import common.recommender as recommender


# MentalHealthError: an exception occurred.

def index(request):

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Generate counts of some of the main objects
    num_places = Place.objects.all().count()
    num_users = User.objects.count()

    context = {
        'num_users': num_users,
        'num_places': num_places,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'common/index.html', context=context)


class UserPlaceData(View):

    def get(self, request, *args, **kwargs):

        place_freq = {}

        for c in Condition.objects.all():
            if request.user.id == c.profile.user.id:
                title = Place.objects.get(id=c.place_id).title
                if place_freq.__contains__(title):
                    place_freq[title] += 1
                else:
                    place_freq[title] = 1

        labels = list(place_freq.keys())
        default_items = list(place_freq.values())

        data = {
            "labels": labels,
            "default": default_items,
        }

        return JsonResponse(data)


class PlaceListView(generic.ListView):
    model = Place
    paginate_by = 10
    context_object_name = 'place_list'
    template_name = 'common/place_list.html'

    def get_queryset(self):
        return Place.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(PlaceListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        # context['some'] = 'data'
        return context


class PlaceDetailView(View):

    def get(self, request, **kwargs):
        # from django.shortcuts import get_object_or_404
        place = get_object_or_404(Place, pk=kwargs.get('pk'))
        votes = list(place.place_votes.all().order_by('rate'))
        avg_rate = sum(vote.rate for vote in votes) / (len(votes) if votes else 1)
        if not avg_rate:
            avg_rate = place.rate

        place.rate = avg_rate
        place.save()
        vote_form = VoteForm()
        condition_form = ConditionForm

        return render(request, 'common/place_detail.html', context={'place': place,
                                                                    'vote_form': vote_form,
                                                                    'condition_form': condition_form})

    def post(self, request, **kwargs):

        # create a form instance and populate it with data from the request:
        vote_form = VoteForm(request.POST)
        condition_form = ConditionForm(request.POST)

        # check whether it's valid:
        if vote_form.is_valid():
            current_user = Profile.objects.get(user=request.user.id)
            place = get_object_or_404(Place, pk=kwargs.get('pk'))

            rate = vote_form.cleaned_data['your_vote']

            if condition_form.is_valid():
                cond = condition_form.save(commit=False)
                cond.place = place
                cond.profile = current_user
                print(cond)
                cond.save()
            vote, created = Vote.objects.update_or_create(profile=current_user,
                                                          place=place,
                                                          defaults={'profile': current_user,
                                                                    'place': place,
                                                                    'rate': rate})

            # redirect to a new URL:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])

        return render(request, 'common/place_detail.html', {'vote_form': vote_form})


def export(request):
    person_resource = ConditionResource()
    dataset = person_resource.export()
    response = HttpResponse(dataset.json, content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="conditions.json"'
    return response


@method_decorator(csrf_exempt, name='dispatch')
class SuggestionView(View):
    success_url = '/'
    template_name = 'common/suggestion.html'

    def get(self, request, *args, **kwargs):
        users = Profile.objects.all()
        return render(request, self.template_name, {'users': users})

    def post(self, request):
        users = []
        conds = []

        for user_id in request.POST:
            user = User.objects.get(id=user_id)
            users.append(user)
            conds.append(user.profile.profile_conds.all())

        if len(users) == 0:
            message ='Invalid number of users. Please select at least one user to go to the lunch.'
            return render(request, 'common/ajax_data.html', context={'message': message,
                                                                     'place': 'NULL'
                                                                     })
        else:
            context = decisiontree.place_prediction(conds)
            if not context == -1:
                request.session['freq_dict'] = context['freq_dict']
                cond_info = self.get_cond_info(context['max_freq_conds'])
                request.session['cond_info'] = cond_info
                place_id = context['place_id']
                score = context['score']*100
                place = Place.objects.get(id=place_id)
                return render(request, 'common/ajax_data.html', context={'users': users,
                                                                         'place': place,
                                                                         'score': score,
                                                                         'cond_info': cond_info,
                                                                         'cond_count': context['total_cond_count']
                                                                         })
            else:
                message = 'No records found.'
                return render(request, 'common/ajax_data.html', context={'users': users,
                                                                         'place': 'NULL',
                                                                         'message': message
                                                                         })

    def get_cond_info(self, max_freq):
        print(max_freq)
        pay = (choices.PAY_CHOICES[max_freq[0]-1])[1]
        time = (choices.TIME_CHOICES[max_freq[1]-1])[1]
        kitchen = (choices.KITCHEN_CHOICES[max_freq[2]-1])[1]
        hunger = (choices.HUNGER_CHOICES[max_freq[3]-1])[1]

        cond_info = {'pay': pay,
                     'time': time,
                     'kitchen': kitchen,
                     'hunger': hunger}
        return cond_info


@method_decorator(csrf_exempt, name='dispatch')
class SuggestionViewData(View):

    def get(self, request, *args, **kwargs):

        freq = request.session.get('freq_dict')
        cond_info = request.session.get('cond_info')

        labels = [cond_info['pay'], cond_info['time'], cond_info['kitchen'], cond_info['hunger']]
        default_items = [freq['pay'], freq['time'], freq['kitchen'], freq['hunger']]
        data = {
            "labels": labels,
            "default": default_items,
        }

        return JsonResponse(data)


class ProfileView(View):

    def get(self, request, **kwargs):
        current_user = Profile.objects.get(user=request.user.id)
        cur_user_votes = current_user.profile_votes.all()

        recommender.read_database()
        recommended_places = recommender.find_knn(current_user.id)
        count = len(recommended_places)

        context = {
            'current_user': current_user,
            'recommended_places': recommended_places,
            'rec_places_count': count,
            'cur_user_votes': cur_user_votes,
        }

        return render(request, 'common/profile.html', context=context)
