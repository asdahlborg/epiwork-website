1. Pull the latest version of the framework code from the git repository.

    $ git pull

2. Set the `MOBILE_INTERFACE_ACTIVE` variable in the `settings.py` file.

    MOBILE_INTERFACE_ACTIVE = True

3. See the [http://egg.science.uva.nl/redmine/wiki/epidb/WebsiteQuickStart](Quickstart
Guide) on the Redmine server for how to set up the website framework.  Follow
the instructions until you have a running local server.

    $ ./bin/django runserver

4. In a browser to the admin server

    http://localhost:8000/admin/auth/user/

5. Add two users.  One with username `ema` and password `emapass`.  This will
be the user who is authorised to access the Epiwork Mobile Application API.
Also add another user with a username, name and password of your choice.

6. Find the `global_id` for the username you added:

    $ ./bin/django shell

    In [1]: from apps.survey.models import SurveyUser

    In [2]: sus = SurveyUser.objects.all()

    In [3]: sus[len(sus)-1].global_id

    Out [3]: u'b9e8353b-e113-4b03-856f-c118e0b70666'
    
    In [4]: from apps.survey.api.utils import code_hash

    In [5]: code_hash(u'b9e8353b-e113-4b03-856f-c118e0b70666')

    Out [5]: '427621639782'

    In [6]: quit()

7. Edit the file `apps/survey/api/maketest.py` to give the
`activation_code` variable the value you found in the previous step. In the
above case, the activation_code` you require is `'427621639782'`

8. Use the `maketest.py` script to generate two test files `test.sh` and
`test.html`

    $ cd apps/survey/api

    $ python maketest.py

9. From the command line you can run the file `test.sh`

    $ bash test.sh

10. Open your browser at the file `test.html` and click on the links there.

11. Confirm that the survey response POSTed is in the response queue:

    $ echo "select * from survey_responsesendqueue;" | sqlite3 ../../../../../ggm.db
