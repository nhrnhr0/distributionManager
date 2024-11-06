from django.shortcuts import render
from collections import defaultdict

from collections import defaultdict

# Input data with categories
# data = [
#     ["1,1,2020", 1, "g1", "c1"],
#     ["2,1,2020", 3, "g1", "c1"],
#     ["3,1,2020", 1, "g2", "c1"],
#     ["4,1,2020", 4, "g1", "c1"],
#     ["5,1,2020", 10, "g2", "c1"],
#     ["5,1,2020", 3, "g1", "c1"],
#     ["5,1,2020", 7, "g3", "c2"]
# ]

# # Dictionary to hold the last known count of each group
# group_counts = defaultdict(int)
# # Dictionary to hold the category for each group
# group_categories = {}
# # Dictionary to hold the cumulative counts for each date and category
# date_totals_by_category = defaultdict(lambda: defaultdict(int))

# # Process each entry
# for entry in data:
#     date, count, group_id, category = entry
#     # Update the group count
#     group_counts[group_id] = count
#     # Store the category for the group
#     group_categories[group_id] = category
#     # Calculate the totals for each category
#     category_totals = defaultdict(int)
#     for group, count in group_counts.items():
#         category_totals[group_categories[group]] += count
#     # Store the total for the current date and category
#     for cat, total in category_totals.items():
#         date_totals_by_category[date][cat] = total

# # Convert the dictionary into a sorted list of results by date and category
# result = sorted([[date, cat, total] for date, totals in date_totals_by_category.items() for cat, total in totals.items()])

# # Print the result
# for row in result:
#     print(row)


from counting.models import MessagesResponsesCount,WhatsappGroupSizeCount,TelegramGroupSizeCount
from django.http import JsonResponse
# Create your views here.

# def api_dashboard_whatsapp_group_count(request):
#     # Get the data
#     data = WhatsappGroupSizeCount.objects.select_related('session','group').prefetch_related('group__whatsapp_categories').all()
#     results = get_group_count(data)
#     # return json response
#     return JsonResponse(results, safe=False)
    
'''
    Function to get the group count
    data: quertset of WhatsappGroupSizeCount/TelegramGroupSizeCount
    group_type: type of group (whatsapp/telegram)
'''
def get_group_count(data, group_type='whatsapp'):
    group_counts = defaultdict(int)
    # Dictionary to hold the category for each group
    group_categories = {}
    # Dictionary to hold the cumulative counts for each date and category
    date_totals_by_category = defaultdict(lambda: defaultdict(int))
    
    # Process each entry
    for entry in data:
        date, count, group_id = entry.session.date, entry.count, entry.group.id#, entry.group.whatsapp_categories.all().first().name
        category = None
        if group_type == 'whatsapp':
            category = entry.group.whatsapp_categories.all()[0].name if entry.group.whatsapp_categories.count() else None
        elif group_type == 'telegram':
            category = entry.group.telegram_categories.all()[0].name if entry.group.telegram_categories.count() else None
        
        if not category:
            continue
        # Update the group count
        group_counts[group_id] = count
        # Store the category for the group
        group_categories[group_id] = category
        # Calculate the totals for each category
        category_totals = defaultdict(int)
        for group, count in group_counts.items():
            if count:
                category_totals[group_categories[group]] += count
        # Store the total for the current date and category
        for cat, total in category_totals.items():
            date_totals_by_category[date][cat] = total
            
    # Convert the dictionary into a sorted list of results by date and category
    result = sorted([[date, cat, total] for date, totals in date_totals_by_category.items() for cat, total in totals.items()])
    return result