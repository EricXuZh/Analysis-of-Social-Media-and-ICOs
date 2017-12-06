import lxml.html as lh
import requests
import time
import StatsAnalysis
import praw

# Data file holding ICO data
ICO_text = open("ICOData2.txt", "w")
ICO_text_stored = open("ICOData_DONOT.txt", "r")
names = StatsAnalysis.get_name(ICO_text_stored)

reddit = praw.Reddit(client_id='2cNexwu4N3vAlg', client_secret='iH6NEiJp2yryr2Kz9_YBEfQj_mU',
                     password='12345678E', user_agent="Getting # of Subscribers by /u/DonkeyDiCs",
                     username='DonkeyDiCs')

print(str(reddit.subreddit("mercuryprotocol").subscribers))


def further_scrapes(url):
    icodrop_page = requests.get(url)
    icodrop_page_tree = lh.fromstring(icodrop_page.content)
    print("Called individual ICO page".rstrip("\n") + ", ")

    soc_links = icodrop_page_tree.cssselect("[class = 'soc_links']")[0].getchildren()
    frt = ["NA", "NA", "NA", str(len(soc_links))]

    for e in soc_links:
        frt = find_members(e.get('href'), frt)

    for oneof in range(len(frt)):
        if frt[oneof] == "NA":
            frt[oneof] = "0"

    for oneof in frt:
        ICO_text.write(oneof.rstrip('\n') + ', ')

    print("finished")


def remove_unneccessary(string):
    return_string = ""

    for character in string:
        if 48 <= ord(character) <= 57:
            return_string += character

    return return_string


def find_members(url, big_three):
    if 'facebook' in url:
        print("Called Facebook".rstrip("\n") + ", ")
        fb_page = requests.get(url)
        fb_page = lh.fromstring(fb_page.content)

        if len(fb_page.cssselect("[class = '_4bl9']")) == 0:
            big_three[0] = "0"
        else:
            followers = fb_page.cssselect("[class = '_4bl9']")[0].text_content().strip()
            number_of_followers = remove_unneccessary(followers)

            big_three[0] = number_of_followers

    if 'reddit' in url:
        subreddit_name = ""

        if url[len(url) - 1] == "/":
            tempstring = url[:len(url) - 1]
        else:
            tempstring = url

        print("called Reddit".rstrip("\n") + ", ")

        for character in tempstring[::-1]:
            if character != "/":
                subreddit_name += character
            else:
                subreddit_name = subreddit_name[::-1]
                break

        try:
            big_three[1] = str(reddit.subreddit(subreddit_name).subscribers)
        except:
            big_three[1] = "0"

    if 'twitter' in url:
        print("called Twitter".rstrip("\n") + ", ")
        twitter_page = requests.get(url)
        twitter_page = lh.fromstring(twitter_page.content)
        followers_t = twitter_page.cssselect("[data-nav = 'followers']")

        if len(followers_t) == 0:
            big_three[2] = "0"
        else:
            big_three[2] = followers_t[0].cssselect("[class = 'ProfileNav-value']")[0].get("data-count")

    return big_three


# Request URL that hosts statistics for individual ICOs that have ended
page = requests.get("https://icodrops.com/category/ended-ico/")
page_tree = lh.fromstring(page.content)  # Convert it into a readable tree

icodrop_links = page_tree.cssselect("[class = 'col-md-12 col-12 a_ico']")  # Get list of all ended ICOs
counter = 0
for ico in icodrop_links:
    name_of_ico = ico.cssselect("[class = 'ico-main-info']")[0].getchildren()[0].text_content().strip().rstrip('\n')
    if len(ico.cssselect("[class = 'notset']")) == 0 and name_of_ico not in names:
        # Ensure that ICO has a pecuniary goal to fulfill and has not already been scraped
        time.sleep(30)
        ICO_text.write(  # Get Name of the ICO
            name_of_ico + ', ')
        further_scrapes(ico.cssselect("[id = 'ccc']")[0].get('href'))
        ICO_text.write((remove_unneccessary(ico.cssselect('''[class = "prec"]''')[0].text_content()) + ', '
                        + remove_unneccessary(
            ico.cssselect("[id = 'new_column_categ_invisted']")[0].getchildren()[0].text_content().strip()) +
                        ', ' + remove_unneccessary(ico.cssselect("[id = 'categ_desctop']")[0].text_content().strip()))
                       + '\n')
    elif (len(ico.cssselect("[class = 'notset']")) == 1 and name_of_ico not in names and
                  ico.cssselect("[id = 'new_column_categ_invisted']")[0].getchildren()[
                      0].text_content().strip() != "Pending"):
        time.sleep(30)
        ICO_text.write(  # Get Name of the ICO
            name_of_ico + ', ')
        further_scrapes(ico.cssselect("[id = 'ccc']")[0].get('href'))
        ICO_text.write(("N/A" + ', '
                        + remove_unneccessary(
            ico.cssselect("[id = 'new_column_categ_invisted']")[0].getchildren()[0].text_content().strip())
                        + '\n'))
    counter += 1
    print(counter)

ICO_text.close()
exit()
