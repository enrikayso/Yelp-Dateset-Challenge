-- numCheckins
update business
set numcheckins = business_checkins.nci
from Business as business_alias inner join
    (
        select business_id, count(time) nci
        from checkins
        group by business_id
    ) business_checkins
    on business_checkins.business_id = business_alias.business_id
where business_checkins.business_id = business.business_id

-- numTips
update business
set numtips = business_tips.nt
from business as business_alias inner join
    (
        select business_id, count(tipdate) nt
        from tip
        group by business_id
    ) business_tips
    on business_tips.business_id = business_alias.business_id
where business_tips.business_id = business.business_id

-- totalLikes
update users
set totallikes = user_tips.tl
from users as user_alias inner join
    (
        select user_id, sum(likes) tl
        from tip
        group by user_id
    ) user_tips
    on user_tips.user_id = user_alias.user_id
where user_tips.user_id = users.user_id

-- tipCount
update users
set tipcount = user_tips.tc
from users as user_alias inner join
    (
        select user_id, count(tipdate) tc
        from tip
        group by user_id
    ) user_tips
    on user_tips.user_id = user_alias.user_id
where user_tips.user_id = users.user_id