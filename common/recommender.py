import math

from common.models import Profile, Vote, Place

titles: ["id",
         "profile",
         "place",
         "rate",
         "vote_datetime"]

users = {}
places_id = Place.objects.values_list('id', flat=True)


def read_database():

    votes = Vote.objects.all()

    for vote in votes:
        u_id = vote.profile.id
        u_name = Profile.objects.get(pk=u_id).user.first_name

        place = vote.place_id
        rate = vote.rate
        if users.__contains__(u_name):
            users[u_name]['votes'][place] = rate
        else:
            users[u_name] = {}
            users[u_name]['votes'] = {}
            for place_id in places_id:
                users[u_name]['votes'][place_id] = -1
            users[u_name]['id'] = u_id
            users[u_name]['votes'][place] = rate

    for name in users.keys():
        print(name, users[name]['id'], users[name]['votes'])
    return users


def find_knn(uid):
    rec_places_list = []
    name = Profile.objects.get(pk=uid).user.first_name
    similarity_scores = {}
    print("Logged-in user: " + name + "\n")

    for user in users:
        other_name = user
        if other_name != name:
            sim = euclidean_distance(name, other_name)
            similarity_scores[other_name] = sim
        else:
            similarity_scores[other_name] = -1

    for key in similarity_scores.keys():
        if not similarity_scores[key] == -1:
            print(key, similarity_scores[key])

    for place_id in places_id:
        place_title = Place.objects.get(pk=place_id).title
        if users[name]['votes'][place_id] == -1:
            weighted_sum = 0
            sim_sum = 0
            for f_name in similarity_scores.keys():
                sim = similarity_scores[f_name]
                ratings = users[f_name]['votes']
                rating = ratings[place_id]
                if not rating == -1:
                    weighted_sum += rating * sim
                    sim_sum += sim
            stars = round(weighted_sum/sim_sum, 2)
            if stars >= 2:
                rec_places_list.append(Place.objects.get(pk=place_id))
            print('Place id: ' + str(place_id) + ", " + place_title + ": " + str(stars))

    return rec_places_list


def euclidean_distance(name, other_name):
    ratings1 = users[name]['votes']
    ratings2 = users[other_name]['votes']

    sum_squares = 0
    for place_id in places_id:
        rating1 = ratings1[place_id]
        rating2 = ratings2[place_id]
        if rating1 != -1 and rating2 != -1:
            diff = rating1 - rating2
            sum_squares += diff * diff

    d = math.sqrt(sum_squares)
    similarity = 1 / (1+d)
    return similarity
