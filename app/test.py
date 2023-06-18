
check  = [   first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        address = request.form.get('address')
        district = request.form.get('district')
        state = request.form.get('state')
        country = request.form.get('country')
        pincode = request.form.get('pincode')
        email = request.form.get('email')
        phone = request.form.get('phone')
        areaofintrest = request.form.get('areaofintrest')
        profession = request.form.get('profession')
        availability = request.form.get('availability') ]

for i in check:
    print(i)