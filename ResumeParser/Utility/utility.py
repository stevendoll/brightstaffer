def convert_date_to_duration(resume):

    months = {'January':1,
              'February':2,
              'March':3,
              'April':4,
              'May':5,
              'June':6,
              'July':7,
              'August':8,
              'September':9,
              'October':10,
              'November':11,
              'December':12
              }
    for index, career in enumerate(resume.career_history):
        dates = [ entity[0] for entity in career if entity[1]=='DATE']
        if dates[0] == 'Present':
            resume.career_history[index].append((dates[1] + '-' + dates[0],'Duration',-1))
        elif dates[1] == 'Present':
            resume.career_history[index].append((dates[0] + '-' + dates[1],'Duration',-1))
        else:
            year1, month1, year2, month2 = int(dates[0].split()[1]), \
                                           months[dates[0].split()[0]], \
                                           int(dates[1].split()[1]), \
                                           months[dates[1].split()[0]]
            if year1 < year2 or (year1 == year2 and month1 < month2):
                resume.career_history[index].append((dates[0] + '-' + dates[1],'Duration',-1))
            else:
                resume.career_history[index].append((dates[1] + '-' + dates[0],'Duration',-1))