## RELEASE NOTES

### Version 1.0.1 - February 11, 2019

**NEW**
- **Model** - Add `demo` attribute to video data model #1
- **Feature** - Add demo lessons #2
- **Model** - Create video collection data models #8
- **Model** - Add `restricted_permit` attribute to device data model #9
- **Feature** - Only permitted devices can access restricted videos #10
- **Feature** - Add VB demo lessons, Y-GRE demo lessons, and Y-GRE test reviews #11
- **Model** - Add device lesson type data model #13
- **Model** - Add `view_point` attribute to lesson type data model #19
- **Model** - Add `login_required` attribute to lesson type data model #20
- **Template** - Add template macro `placeholder_widget()` #21
- **Feature** - Adopt Y-System user migration API #30
- **Feature** - Adopt Y-System progress report API #31
- **Feature** - Adopt Y-System user authentication API #32
- **Feature** - Authenticate user via Y-System #37
- **Feature** - Email production server errors to system operator #39
- **Model** - Add `synchronized` attribute to punch data model #40
- **Model** - Add `progress_threshold` attribute to lesson data model #41
- **Feature** - Adopt Y-System lesson access API #42

**IMPROVED**
- **Model** - Change `demo` attribute of video data model to `restricted` #7
- **Model** - Remove user creation data model #14
- **Model** - Change `created_at` attribute of user data model to `imported_at` #15
- **Model** - Remove `restricted_permit` attribute from device data model #16
- **Model** - Remove `restricted` attribute from video data model #17
- **Model** - Remove `order` attribute from lesson data model #18
- **Feature** - Simplify user profile overview page contents #22
- **Template** - Adopt static assets hosted on static.y-english.cn #25
- **Form** - Rearrange form modules #27
- **View** - Rearrange view modules #28
- **Model** - Remove ID type data model #33
- **Model** - Remove gender data model #34
- **Model** - Remove `id_number`, `id_type_id` and `gender_id` attributes from user data model #35
- **Feature** - Remove Y-VOD token authentication feature #36

**FIXED**
- **Feature** - Playback rate changes are not taken into account in total video play time calculation #23
- **Feature** - Synchronized punches continue to synchronize #50
- **Feature** - Punch synchronization failure due to existing unsynchronized punches #54

### Version 1.0.0 - December 24, 2018

**IMPORTANT NOTE**
> Boom! Excited!
