#!/usr/bin/env python3
"""Tag every glyph with a Huge Icon Set category and rewrite icons.js.

    python3 tools/categorize.py

Categories come from the Huge Icon Set v2.0 sheet. The font ships no category
metadata, so these are keyword rules over the icon name — first match wins, so
specific rules must sit above general ones.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (category, [substrings]) — ordered, first match wins.
RULES = [
    ('Islamic',        ['mosque','quran','kaaba','ramadhan','salah','adzan','hijab','niqab','muslim','allah','muhammad','haji','halal','zakat','tasbih','sujood','ruku','wudu','bedug','ketupat','prayer-rug','rub-el-hizb','keffiyeh','eid-','alms','dua','camel','lantern','charity','dates']),
    ('Crypto',         ['bitcoin','ethereum','blockchain','litecoin','ripple','peer-to-peer','mining-','centralized','stake','ico','shield-blockchain','usdt','coinbase']),
    ('Weather',        ['sun-cloud','moon-cloud','cloud-','cloud','rain','snow','storm','tornado','tsunami','thermometer','humidity','rainbow','sunrise','sunset','wind','fahrenheit','celsius','soil-','uv-','moonset','avalanche','gibbous','desert','fast-wind','slow-wind','sparkles','zap','sun-','moon','eclipse','stars','hailstone']),
    ('Wifi',           ['wifi','signal-','hotspot','internet','cellular-network','router','wireless','rss','smartphone-wifi','smartphone-lost','secured-network','shared-wifi','no-internet','gps-','satellite']),
    ('Hands',          ['hand-pointing','pointing-','swipe-','touch','tap-','drag-','hold-','shaka','finger','clapping','waving-hand','punch','victory','ok-finger','sign-language','love-korean','touchpad','do-not-touch','hand-prayer']),
    ('Mouse',          ['mouse','cursor']),
    ('Mathematics',    ['equal-sign','not-equal','inequality','summation','root-','n-th-root','square-root','sine','cosine','tan','cos','sin','pi-','insert-pi','remove-pi','alpha','beta','infinity','congruent','approximately','more-or-less','plus-minus','minus-plus','plus-sign','minus-sign','multiplication','divide-sign','percent','function','x-variable','brecket','bracket','parabola','hyperbole','cylinder','cone-','sphere','pyramid','prism','cube','octagon','hexagon','pentagon','rhombus','parallelogram','trapezoid','angle','acute','obtuse','reflex','radius','diameter','matrix','absolute','segment','coordinate','cordinate','abacus','calculator','greater-than','less-than','left-triangle','right-triangle','square-circle','square-square','triangle-0']),
    ('Emojis',         ['sad-','angry','laughing','kissing','angel','crying','confused','crazy','dead','drooling','displeased','evil','flushed','grimacing','grinning','happy','in-love','meh','monocle','mute','nerd','neutral','pensive','relieved','senseless','shocked','silence','sing-','sleeping','smile','smart','star-face','sunglasses','surprise','suspicious','tired','tongue','unamused','unhappy','vomiting','wink','worry','look-','kid','bot','drool']),
    ('Medical',        ['medic*','hospital','dental','blood','bandage','ampoule','injection','stethoscope','cardiogram','vaccine','prescription','x-ray','wheelchair','disability','kidney','liver','lungs','bone','broken-bone','dna','sperm','labs','caduceus','first-aid','give-blood','give-pill','treatment','digestion','health','covid','aids','clinic','protection-mask','medical-mask','hand-sanitizer','mortar','nose','ear','eye','skull','brain-0','patient','doctor','tissue-paper','pill','syringe','bacteria','dropper']),
    ('Gaming',         ['joystick','game-controller','pacman','pokemon','pokeball','nintendo','super-mario','tetris','chess','dice','domino','puzzle','cards-','clubs-','spades','joker','block-game','tic-tac-toe','ds3-tool','gameboy','video-console','vr-glasses','knight-shield','greek-helmet','spartan-helmet','armored-boot','sword-','gun','bomb','potion','maze','castle','angry-bird','adventure','gem','kite','billiard','pool-table','bowling','racing-flag']),
    ('Gym',            ['workout','dumbbell','treadmill','yoga','kettlebell','boxing','punching-ball','gymnastic','body-part','body-weight','equipment-','expander','skipping-rope','push-up','tape-measure','weight-scale','hand-grip','locker','wellness','running-shoes','towels','pool']),
    ('Foods',          ['pizza','burger','hamburger','sushi','taco','bread','cheese','cupcake','cookie','croissant','doughnut','ice-cream','milk','noodle','spaghetti','steak','sausage','shellfish','prawn','crab','octopus','fish-food','egg','carrot','broccoli','apple','banana','apricot','avocado','cherry','grapes','orange','watermelon','pumpkin','corn','nut','honey','chocolate','popcorn','biscuit','birthday-cake','cinnamon','french-fries','hotdog','dim-sum','mochi','rice-bowl','soda','soft-drink','drink','tea','coffee','bubble-tea','cotton-candy','lollipop','snail','yogurt','pie','fry','organic-food','natural-food','vegetarian','bbq','chicken-thighs','cheese-cake','mushroom','dish-','plate','cake','beef','ham','salad','soup','candy']),
    ('Kitchen',        ['kitchen','chef','knife','knives','spoon','fork','whisk','spatula','pan-','pot-','oven','microwave','refrigerator','fridge','blender','mixer','beater','rolling-pin','jar','kettle','apron','glove','matches','gas-stove','dish-washer','cook-book','pizza-cutter','chopstick']),
    ('Furnitures',     ['sofa','chair','table','desk','bed','wardrobe','cabinet','dressing-table','bookshelf','lamp','candelier','curtains','mirror','toilet','bathtub','sink','rocking-chair','vintage-clock','hanging-clock','office-chair','television-table','cleaning-bucket','flower-pot','hot-tube','terrace','garage','study-','door','stairs','shelving','pillow','armchair','blinds']),
    ('Buildings',      ['building','house','hotel','city','castle','mosque-0','church','factory','tower','pyramid-m','colosseum','eiffel','taj-mahal','pisa','borobudur','monas','trulli','yurt','hut','cottage','plaza','patio','barns','bridge','island','lake','lighthouse','dome','fortress','guest-house','real-estate','university','school','library','apartment','villa','duplex','warehouse','cafe','restaurant','theater','stadium','berlin','chrysler','china-temple','india-gate','torri-gate','washington','burj','cayan','ferris-wheel','mayan','twin-tower','beach','fire-pit','pavilon','central-shaheed','the-prophets']),
    ('Logos',          ['adobe','apple','google','facebook','twitter','instagram','linkedin','youtube','tiktok','snapchat','whatsapp','telegram','discord','slack','figma','github','gitlab','notion','dropbox','spotify','netflix','amazon','microsoft','meta','threads','reddit','pinterest','tumblr','vimeo','twitch','behance','dribbble','medium','quora','flickr','wordpress','shopify','stripe','paypal','payoneer','visa','master-card','skype','zoom','teamviewer','team-viewer','wechat','viber','line','imo','bing','safari','chrome','android','framer','webflow','codesandbox','codepen','bootstrap','boostrap','react','python','java','php','npm','docker','kickstarter','capcut','wps-office','lottiefiles','envato','fiverr','upwork','airbnb','uber','waze','yelp','xing','vk','vine','wattpad','wikipedia','scribd','slideshare','soundcloud','lastfm','last.fm','stumbleupon','swarm','foursquare','deviantart','digg','forrst','bebo','plaxo','picasa','periscope','iconjar','flaticon','mymind','creative-market','shutterstock','unsplash','pexels','hangout','messenger','office-365','play-store','app-store','claude','openai','copilot','grok','gemini','deepseek','mistral','qwen','perplexity','nike','tinder','trello','path','ico n','html-5','css3','typescript','tailwind','shadcn','replit','loom','leetcode','hackerrank','gitbook','arc-browser','brandfetch','datev','klarna','mollie','wise','crowdfunding-l','blogger','x-ellipse','x-rectangle','zsh','bash']),
    ('Git',            ['git-','github','gitlab','repository','pipeline']),
    ('Programming',    ['server*','code','programming','developer','console','sql','database','api','binary','variable','source-code','inspect-code','step-','property-','software','translate','translation','language-skill','command-line','incognito','message-programming','web-design','web-programming','regex','terminal']),
    ('Security',       ['lock','security','shield','finger-print','fingerprint','iris-scan','password','firewall','authorized','access','encrypt','cctv','id-verified','id-not','circle-password','qr-code','protection','safe','danger','key-','key0','vault','biometric','two-factor','forgot-password','reset-password','recovery']),
    ('Search',         ['search','zoom-in-area','zoom-out-area','magnif*']),
    ('Settings',       ['setting*','configuration','customize','toggle','preference','sliders','setup','wrench','system-update','installing-updates','list-setting','gears','cog','tools','toolbox','repair']),
    ('Space',          ['astronaut','rocket','spaceship','satellite-0','galaxy','saturn','jupiter','orbit','asteroid','comet','alien','ufo','moon-landing','black-hole','constellation','solar-system','earth','falling-star','monster','space','planet','nebula','telescope']),
    ('Science + Technology', ['atom','molecule','cells','gravity','pendulum','nano','magnet','submerge','bounding-box','siri','wind-turbine','test-tube','chemistry','physics','microscope','beaker','flask','acceleration','prism-','hologram','robot','machine-robot','chip','cpu','gpu','microchip','neural','quantum']),
    ('Logistics',      ['truck','delivery','shipping','cargo','container','package','courier','forklift','lift-truck','tow-truck','garbage-truck','scooter','pickup','van','taxi','bus-','train','tram','metro','subway','airplane','plane','helicopter','ferry','boat','ship','submarine','zeppelin','hot-air-balloon','bicycle','motorbike','car-','caravan','camper','tractor','crane','drone','ambulance','police-car','fire-truck','school-bus','golf-cart','toy-train','traffic','road','accident','fuel-station','parking','steering','transmission','tire','engine','shipment','freight','trolley']),
    ('Users',          ['user','profile','account','contact-','people','person','man','woman','child','infant','elder','student','teacher','employee','team','group']),
    ('Communication',  ['call','phone','mail','message','chat','bubble-chat','comment','inbox','telephone','dialpad','conversation','customer-service','customer-support','sent','voice','mic-','megaphone','broadcast','notification-0','contact']),
    ('Alert + Notification', ['alert','notification','spam','radioactive','warning','help-circle','help-square','information','exclamation','siren','bell']),
    ('Check',          ['checkmark*','tick-','validation','verified','approval']),
    ('Arrows',         ['chevron*','corner-','arrow','circle-arrow','square-arrow','curvy-','scroll-point','unfold-','transition-','move-to','navigation-0']),
    ('Add + remove',   ['add-','remove-','delete','cancel-','clear-','eraser','waste','restore-bin','unavailable','trash']),
    ('Awards',         ['medal*','award*','crown*','laurel*','champion','honor','honour*','ranking','trophy','new-releases','certificate','badge*','ribbon']),
    ('Bookmarks',      ['bookmark','favourite','favorite','star','heart','tag-','label','thumbs','collections']),
    ('Animation',      ['keyframe*','ease-','bounce-','motion-','liner','transition','move-right','move-left','move-top','move-bottom']),
    ('AI',             ['ai-','artificial-intelligence','chat-bot','chatgpt','machine-learn','robotic','neural','prompt']),
    ('Dashboard',      ['dashboard','discover-']),
    ('Date + Time',    ['calendar','clock','time-','timer','alarm','hourglass','stop-watch','watch-','digital-clock','schedule','date-','smart-watch','appointment']),
    ('Devices',        ['smart-phone','smartphone','tablet','laptop','computer','monitor','keyboard','printer','tv-','modern-tv','television','airpod','headphone','headset','speaker','camera-','radio','usb','sd-card','simcard','hdd','hard-drive','floppy','database-0','cd','ipod','gameboy','mirroring','remote-control','screen-','send-to-mobile','virtual-reality','3d-view','three-d-view','pen-connect','battery','bluetooth','airdrop','airplane-mode','airplay','external-drive','data-recovery','memory','fan-','vacuum','washing-machine','heater','smart-ac','electric-plugs','plug','socket','webcam','projector']),
    ('Download + Upload', ['download','upload','cloud-download','cloud-upload','export','import']),
    ('Files',          ['file','folder','doc-','pdf','csv','txt','xml','xsl','zip','rar','png','jpg','svg','gif','raw-','mp3','mp4','tiff','wav','ppt','xls','archive','catalogue','license','scroll','policy','floor-plan','news-0']),
    ('Editing',        ['text-','paragraph','heading','pen-tool','pencil','paint','brush','eraser-','crop','layer*','align-','distribute-','pathfinder','stroke-','flip-','rotate','group-','ungroup','magic-wand','lasso','color-picker','colors','swatch','gradient','blur','blend','opacity','transparency','artboard','canvas','bend-tool','join-','cap-','dashed-line','solid-line','edge-style','skew','perspective','anchor-point','select-','list*','move-','alphabet-','between-','tally*','progress*','selection','quote-','list-view','grid','row-','column-','table-','insert-','left-to-right','right-to-left','letter-spacing','type-cursor','font','italic','bold','underline','strikethrough','superscript','subscript','smallcaps','kerning','tracking','indent','wrap','ruler','scissor','copy-','cut-','paste','undo','redo','refresh','reload','edit-','drawing-','straight-edge','orthogonal','carousel','trapezoid-line','change-screen','character-phonetic','command','covariate','minimize','maximize','resize','move-0','drag-0','signature','stamp-0','ellipse-selection','marquee']),
    ('Layout',         ['layout','border-','sidebar','panel','picture-in-picture','aspect-ratio','frame']),
    ('Menu',           ['menu','more-','dots']),
    ('Media',          ['play','pause','stop','record','next','previous','forward','backward','shuffle','repeat','volume','music-note','playlist','play-list','vynil','vinyl','subtitle','burning-cd','go-backward','go-forward','headphones','film','video','camera-video','podcast','audio','speaker-']),
    ('Image + Camera', ['image','photo','camera','album','film-roll','flash','focus','hdr','closed-caption','open-caption','picture','gallery','frame-']),
    ('Maps',           ['location','map','gps','navigat*','pin','radar','compass','direction','route','latitude','longitude','geo-fence','global','globe','world','street','path-','waypoint']),
    ('Legal',          ['legal','justice','court','judge','police','sheriff','prison','handcuffs','copyright','trademark','wanted','subpoena','auction','podium','agreement','identification','investigation','audit','register','stamp','law','contract','notary']),
    ('Shopping',       ['shopping','store','cart','basket','shop-sign','sale-tag','discount','coupon','voucher','ticket','gift','loyalty','promotion','marketing','trolley','bag-','price','checkout','product']),
    ('Business',       ['chart','analytics','money','dollar','euro','pound','yen','coins','cash','wallet','credit-card','card-exchange','bank','invoice','receipt','payment','profit','budget','tax','briefcase','office','job-','work-','corporate','conference','strategy','start-up','seo','target','estimate','meeting','passport','permanent-job','manager','labor','atm','cashier','piggy-bank','gold','pie-chart','crowdfunding','transaction','exchange','savings','stake-','trade','market','departement','news','brochure','complaint','service','vision','registered','radial','archive-','address-book','at','question','qq-plot','limitation','idea','important-book','auto-conversations','advertisiment','attchment','calculate','computer-dollar','distribution','file-bitcoin','file-euro','file-dollar','file-pound','file-yen','contact-book','customer-service-0','umbrella','tie','trademark-','vision-','waterfall','pay-by-check','saudi-riyal','riyal','dirham','rupee','ruble','franc','lira','peso','won','shekel']),
    ('Education',      ['school','book','education','learning','graduate','graduation','student','teacher','teaching','mentor','knowledge','library','certificate','diploma','mortarboard','physics','chemistry','math','backpack','notebook','pencil-','course','quiz','audio-book','board-math','elearning','online-learning','global-education','share-knowledge','geology','brain','dna-','test-tube','telescope','clip','locker-','stationery','study','moon-','desk-']),
    ('Clothing',       ['shirt','dress','pants','shorts','hoodie','sleeveless','jacket','suit','cardigan','vest','boxer','underpants','sandals','high-heels','shoes','sneaker','socks','hat','cap','cowboy','belt','tie-','bow-tie','necklace','ear-rings','purse','hand-bag','hanger','kurta','turtle-neck','tank-top','jogger','long-sleeve','t-shirt','monocle','glasses','perfume','shampoo','body-soap','blush-brush','hair-','diaper','baby-','breast-pump','safety-pin','clothes','poop','bra','apron-']),
    ('Energy',         ['energy','solar','power','battery-','plug-','electric','recycle','renewable','nuclear','hydro','biomass','wind-power','wind-turbine','fuel','oil-barrel','gas-pipe','water-pump','eco-','chimney','green-house','temperature','atomic','magnet-','save-energy','ev-charging','automotive-battery','batteries']),
    ('Filter + Sorting', ['filter','sort*','preference-']),
    ('Hierarchy',      ['hierarchy','structure','workflow','flowchart','flow','node-','subnode','pyramid-','scheme','pipeline','time-management','org-chart']),
    ('Home',           ['home-','house-','door-']),
    ('Link + Unlink',  ['link','unlink','share','attachment','chain']),
    ('Login + Logout', ['login','logout','log-in','log-out','sign-in','sign-out']),
    ('Notes + Tasks',  ['note','task','sticky-note','notebook','checklist','todo','clipboard','reminder']),
    ('Presentation',   ['presentation','co-present','projector','slide','whiteboard']),
    ('Shapes',         ['circle','square','triangle','hexagon','pentagon','octagon','rhombus','oval','polygon','spirals','seal','diamond','shapes','geometric','rectangular','star-','heart-']),
]

src = (ROOT / 'icons.js').read_text(encoding='utf-8')
ICONS = json.loads(src[src.index('['):src.rindex(']') + 1])

def matches(name: str, key: str) -> bool:
    """Match whole hyphen-segments, not raw substrings.

    A plain `key in name` puts every clock icon in Security, because 'lock'
    lives inside 'clock'. Padding both sides with hyphens makes 'lock' hit
    'circle-lock-01' and miss 'alarm-clock'. Keys ending in '-' stay prefix
    matches, which is how the multi-segment families are written.
    """
    if key.endswith('*'):
        return key[:-1] in name          # explicit stem: medic* -> medicine
    if key.endswith('-') or any(c.isdigit() for c in key):
        return key in name               # explicit partial: ai-, brain-0
    return f'-{key}-' in f'-{name}-'     # whole segment


def categorize(name: str) -> str:
    for cat, keys in RULES:
        for k in keys:
            if matches(name, k):
                return cat
    return 'Other'

# Re-runnable: icons.js may already carry a category from a previous pass.
tagged = [[r[0], r[1], r[2], categorize(r[1])] for r in ICONS]

(ROOT / 'icons.js').write_text(
    'const ICONS=' + json.dumps(tagged, separators=(',', ':')) + ';', encoding='utf-8')

from collections import Counter
counts = Counter(t[3] for t in tagged)
print(f'{len(tagged)} icons tagged into {len(counts)} categories\n')
for cat, n in counts.most_common():
    print(f'  {n:>5}  {cat}')
