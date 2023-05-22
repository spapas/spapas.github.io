Title: AI auto-subtitling
Date: 2023-05-22 13:20
Tags: ai, whisper, whisper.cpp, subtitles, video, auto-subtitling, subtitiling, transcribe
Category: ai
Slug: ai-auto-subtitling
Author: Serafeim Papastefanos
Summary: Auto-subtitling movies with AI

## Introduction

As English is not my native language, I rely on subtitles to fully enjoy and comprehend most movies.
Unfortunately there are a lot of movies that don't include subtitles or the subtitles that I am able
to find are not synchronized with the movie.

In this small post I'll give you some instructions on how to use the newest "AI" trends to automatically 
generate subtitles for a movie. The process does not achive 100% accuracy but it is very good and should definitely allow you to understand what's being said. 

Also, the described process will be very useful to people that do the actual subtitling for new movies since it 
should save them a lot of manual labour. Instead of adding subtitles and timings manually they can use this to generate an automatic subtitle draft and then edit it by hand and ear.

Finally, please notice that all tools described here are free and open source and you should be able to run everything on your PC even if it is very slow and doesn't have a GPU.

*Everything described here is for educational purposes only. Please don't use it to generate subtitles for movies that you don't own or have the rights to do so.*

## Whisper.cpp

For the auto-subtitling we'll use the [whisper.cpp](https://github.com/ggerganov/whisper.cpp) library. This
library can be used to auto-transcribe audio files i.e it gets
audio as input and outputs the text that is being said in the audio.

This library can be compiled on your PC however to avoid complex workflows you can 
[download the binaries for your system](https://github.com/ggerganov/whisper.cpp/releases/tag/v1.4.0). I'd also
recommend to download the BLAS binaries since they should work faster if your system supports them.

After you download the whisper.cpp extract it in a folder of your choice.

Beyond whisper.cpp, you need to download a model that will be used for the transcription.
The simplest way is to go to the hugging face whisper.cpp [model repository](https://huggingface.co/ggerganov/whisper.cpp/tree/main)
and download the model from there. You only need 1 model file. The largest models will give you better results but will be slower and require more resources. I think that the base or small models should be good and fast enough.

I'll give you some test results later to see the differences.

Notice that if your movie is in english you should download the .en models. 

To continue copy the downloaded models in the whisper.cpp folder.

## Extract audio from the movie

The whisper.cpp library requires uncompressed audio (a .wav file) with specific characteristics (a sample rate of 16khz) to work.

To be able to extract that audio from our movie will use [ffmpeg](https://ffmpeg.org/). Download the win64 binaries 
[from here](https://github.com/BtbN/FFmpeg-Builds/releases) (get the `ffmpeg-master-latest-win64-gpl.zip` file) and copy over ffmpeg.exe to the whisper.cpp folder.

Then, to extract the audio from the movie you can use the following command:

```bash
ffmpeg.exe -i "movie.mp4" -f wav -vn -acodec pcm_s16le -ar 16000 -ac 1 "movie.wav"
```
(please change movie.mp4 and movie.wav with the correct names for your movie file).

To understand the command:

* `-i "movie.mp4"`: the input file
* `-f wav`: the output format (a .wav file)
* `-vn`: no video
* `-acodec pcm_s16le`: the audio codec (the correct one for .wav file)
* `-ar 16000`: the sample rate (16khz)
* `-ac 1`: the number of channels (1 for mono, 2 for stereo)
* `"movie.wav"`: the output file

The process should be very fast and will give you a .wav file with the same length as the movie.

## Transcribing the audio

The last step is to do the actual audio transcribing using whisper.cpp. The great thing about whisper.cpp
is that it can directly create .srt (subtitle) files. The command to use is:

```bash
main.exe -osrt -m ggml-base.en.bin -f movie.wav
```

Notice that

*  The whisper.cpp bundle you downloaded should have a main.exe file
* `-osrt`: Generate a .srt file as output
* `-m ggml-base.en.bin`: The model to use for the transcription
* `-f movie.wav`: The input file

The above command will start outputing the text it detects and when it finishes it will generate a `movie.wav.srt`.  You can then use that .srt file to add subtitles for your movie!

## Results

To test the process I used the first 14 minutes of the movie Kill Bill 2 as input. To generate the .wav file I used the following command:

```bash
ffmpeg.exe -i "kb2.mp4" -f wav -vn -acodec pcm_s16le -ar 16000 -ac 1  -ss 00:00:00 -to 00:14:00 "kb2.wav"
```

(please notice the `-ss` and `-to` to select the first 14 minutes of the movie).

This generated a 26 MB wav file. Then I tried the results using
three different models:

* ggml-tiny.en.bin with a size of 77 MB
* ggml-base.en.bin with a size of 147 MB
* ggml-small.en.bin with a size of 488 MB
* ggml-medium.bin with a size of 1533 MB

### ggml-tiny.en.bin

Some stats:

```
whisper_model_load: mem required  =  201.00 MB (+    3.00 MB per decoder)
whisper_model_load: model size    =   73.54 MB

whisper_print_timings:    total time = 166330.89 ms
```

**So time needed was ~ 160 seconds**

And the actual transcription:

```
[00:00:00.000 --> 00:00:03.000]   [MUSIC PLAYING]
[00:00:03.000 --> 00:00:16.480]   Do you finally sit just now?
[00:00:16.480 --> 00:00:19.120]   [MUSIC PLAYING]
[00:00:19.120 --> 00:00:21.480]   No, I can't do.
[00:00:21.480 --> 00:00:27.600]   I'd like to believe you're aware enough even now.
[00:00:27.600 --> 00:00:35.080]   No, that there is nothing suggesting in my actions.
[00:00:35.080 --> 00:00:44.000]   This moment, this is me and my most nice against them.
[00:00:44.000 --> 00:00:47.440]   Well, it's your name.
[00:00:47.440 --> 00:00:52.920]   [MUSIC PLAYING]
[00:00:52.920 --> 00:00:55.120]   But Dad didn't I?
[00:00:55.120 --> 00:00:56.640]   Well, I wasn't.
[00:00:56.640 --> 00:00:58.040]   But it wasn't from lack of trying.
[00:00:58.040 --> 00:01:00.360]   I can tell you that.
[00:01:00.360 --> 00:01:03.600]   Actually, Bill's last bullet put me in a coma.
[00:01:03.600 --> 00:01:07.600]   A coma, I was to lie in for four years.
[00:01:07.600 --> 00:01:09.360]   And I woke up.
[00:01:09.360 --> 00:01:11.280]   I went on with a movie advertisements
[00:01:11.280 --> 00:01:15.720]   for two as a roaring rampage of revenge.
[00:01:15.720 --> 00:01:17.120]   I roared.
[00:01:17.120 --> 00:01:18.800]   And I relanged.
[00:01:18.800 --> 00:01:22.480]   And I got bloody satisfaction.
[00:01:22.480 --> 00:01:26.360]   I've killed a hell of a lot of people to get to this point.
[00:01:26.360 --> 00:01:29.720]   But I have only one more.
[00:01:29.720 --> 00:01:31.760]   The last one.
[00:01:31.760 --> 00:01:35.360]   The one I'm driving to right now.
[00:01:35.360 --> 00:01:38.280]   The only one left.
[00:01:38.280 --> 00:01:42.040]   And when I arrive at my destination,
[00:01:42.040 --> 00:01:44.200]   I have going to kill Bill.
[00:01:44.200 --> 00:01:47.200]   [MUSIC PLAYING]
[00:01:47.200 --> 00:02:10.880]   [MUSIC PLAYING]
[00:02:10.880 --> 00:02:13.480]   Now the incident that happened at the two pines wedding
[00:02:13.480 --> 00:02:17.360]   chapel that put this whole gory story into motion
[00:02:17.360 --> 00:02:20.120]   has since become legend.
[00:02:20.120 --> 00:02:22.800]   Massacre at two pines.
[00:02:22.800 --> 00:02:24.800]   That's what the newspapers called it.
[00:02:24.800 --> 00:02:28.760]   The local TV news called it the El Paso, Texas wedding
[00:02:28.760 --> 00:02:30.920]   chapel massacre.
[00:02:30.920 --> 00:02:32.280]   How it happened?
[00:02:32.280 --> 00:02:33.680]   Who was there?
[00:02:33.680 --> 00:02:36.600]   How many got killed and who killed them?
[00:02:36.600 --> 00:02:40.320]   Changes depending on who's telling the story.
[00:02:40.320 --> 00:02:43.080]   In actual fact, the massacre didn't happen
[00:02:43.080 --> 00:02:45.720]   during a wedding at all.
[00:02:45.720 --> 00:02:48.360]   It was a wedding rehearsal.
[00:02:48.360 --> 00:02:51.800]   Now when we come to the park where I say you make kiss,
[00:02:51.800 --> 00:02:55.120]   the bride, you make kiss, the bride.
[00:02:55.120 --> 00:02:56.960]   But don't stick your tongue in her mouth.
[00:02:56.960 --> 00:03:01.840]   This might be funny to your friends,
[00:03:01.840 --> 00:03:06.440]   but it would be embarrassing to your parents.
[00:03:06.440 --> 00:03:08.200]   We'll try to do strange things.
[00:03:08.200 --> 00:03:11.080]   [LAUGHTER]
[00:03:11.080 --> 00:03:12.040]   Y'all got a song?
[00:03:12.040 --> 00:03:18.000]   How about love me, tender?
[00:03:18.000 --> 00:03:18.840]   I'd play that.
[00:03:18.840 --> 00:03:24.360]   Let me tender be great.
[00:03:24.360 --> 00:03:27.520]   Rufus, he's the man.
[00:03:27.520 --> 00:03:30.640]   Rufus, who was that he used to play for?
[00:03:30.640 --> 00:03:32.640]   Rufus Thomas.
[00:03:32.640 --> 00:03:34.760]   Rufus Thomas.
[00:03:34.760 --> 00:03:35.680]   Rufus Thomas.
[00:03:35.680 --> 00:03:37.080]   I was a dreel.
[00:03:37.080 --> 00:03:38.600]   I was a drifter.
[00:03:38.600 --> 00:03:40.080]   I was a colister.
[00:03:40.080 --> 00:03:41.920]   I was a part of the game.
[00:03:41.920 --> 00:03:43.760]   I was a bar kid.
[00:03:43.760 --> 00:03:48.200]   If they come through Texas, I can play with him.
[00:03:48.200 --> 00:03:50.720]   Rufus, he's the man.
[00:03:50.720 --> 00:03:56.840]   I never forgot anything.
[00:03:56.840 --> 00:04:00.440]   Oh, yes, you forgot the seating arrangements.
[00:04:00.440 --> 00:04:03.200]   Thank you, Mother.
[00:04:03.200 --> 00:04:07.840]   Now the way we normally do this, we have the bride's side,
[00:04:07.840 --> 00:04:09.560]   and then we have the groom's side.
[00:04:09.560 --> 00:04:12.880]   But since the bride ain't got nobody coming,
[00:04:12.880 --> 00:04:16.960]   and the groom's got far too many people coming--
[00:04:16.960 --> 00:04:18.920]   Well, yeah, they're coming all the way from Oklahoma.
[00:04:18.920 --> 00:04:21.600]   [LAUGHTER]
[00:04:21.600 --> 00:04:23.160]   Right.
[00:04:23.160 --> 00:04:27.880]   Well, I don't see no problem with the groom's side
[00:04:27.880 --> 00:04:29.840]   sharing the bride's side.
[00:04:29.840 --> 00:04:30.760]   Do you, Mother?
[00:04:30.760 --> 00:04:32.720]   Not a problem with that.
[00:04:32.720 --> 00:04:38.880]   But honey, you know, it would be good if you had somebody come.
[00:04:38.880 --> 00:04:42.840]   You know, it was a sign of good faith.
[00:04:42.840 --> 00:04:49.400]   Well, I don't have anybody except for Tommy and my friends.
[00:04:49.400 --> 00:04:52.000]   You have no family?
[00:04:52.000 --> 00:04:53.600]   Well, I'm working on changing that.
[00:04:53.600 --> 00:04:55.360]   Mrs. Harmony, we're all the family.
[00:04:55.360 --> 00:04:56.760]   This is Langel's ever going to need.
[00:04:56.760 --> 00:05:01.760]   I don't feel very well in this bitch.
[00:05:01.760 --> 00:05:03.680]   This started to piss me off.
[00:05:03.680 --> 00:05:08.280]   So while you all blather on, I'm going to go outside and get some air.
[00:05:08.280 --> 00:05:10.320]   I'm a Reverend, sorry.
[00:05:10.320 --> 00:05:11.840]   She's going to go out and get some air.
[00:05:11.840 --> 00:05:12.440]   Yeah.
[00:05:12.440 --> 00:05:15.320]   Given her delicate condition, she just needs a few minutes
[00:05:15.320 --> 00:05:15.920]   to get it together.
[00:05:15.920 --> 00:05:16.920]   She'll be OK.
[00:05:16.920 --> 00:05:19.880]   [MUSIC PLAYING]
[00:05:19.880 --> 00:05:23.880]   [MUSIC PLAYING]
[00:05:23.880 --> 00:05:27.880]   [MUSIC PLAYING]
[00:05:27.880 --> 00:05:31.880]   [MUSIC PLAYING]
[00:05:31.880 --> 00:05:35.880]   [MUSIC PLAYING]
[00:05:35.880 --> 00:05:39.880]   [MUSIC PLAYING]
[00:05:39.880 --> 00:05:43.880]   [MUSIC PLAYING]
[00:05:43.880 --> 00:05:47.880]   [MUSIC PLAYING]
[00:05:47.880 --> 00:05:51.880]   [MUSIC PLAYING]
[00:05:51.880 --> 00:05:55.880]   [MUSIC PLAYING]
[00:05:55.880 --> 00:05:59.880]   [MUSIC PLAYING]
[00:05:59.880 --> 00:06:01.880]   [MUSIC PLAYING]
[00:06:01.880 --> 00:06:03.880]   [MUSIC PLAYING]
[00:06:03.880 --> 00:06:05.880]   [MUSIC PLAYING]
[00:06:05.880 --> 00:06:07.880]   [MUSIC PLAYING]
[00:06:07.880 --> 00:06:09.880]   [MUSIC PLAYING]
[00:06:35.880 --> 00:06:37.880]   Hello, kiddo.
[00:06:37.880 --> 00:06:45.880]   How did you find me?
[00:06:45.880 --> 00:06:46.880]   I'm the man.
[00:06:46.880 --> 00:06:54.880]   What are you doing here?
[00:06:54.880 --> 00:06:57.880]   Am I doing?
[00:06:57.880 --> 00:07:02.880]   Well, I'm only going to play my flute.
[00:07:02.880 --> 00:07:05.880]   [MUSIC PLAYING]
[00:07:05.880 --> 00:07:14.880]   This moment, I'm looking at the most beautiful
[00:07:14.880 --> 00:07:18.880]   bright and these old eyes of every scene.
[00:07:18.880 --> 00:07:20.880]   Where are you here?
[00:07:20.880 --> 00:07:21.880]   Nice look.
[00:07:21.880 --> 00:07:26.880]   Are you going to be nice?
[00:07:26.880 --> 00:07:30.880]   I've never been nice my whole life.
[00:07:30.880 --> 00:07:33.880]   But I'll do my best to be sweet.
[00:07:33.880 --> 00:07:42.880]   I was told you, your sweet side is your best side.
[00:07:42.880 --> 00:07:45.880]   I guess that's why you're the only one who's ever seen it.
[00:07:45.880 --> 00:07:51.880]   See, you got a bun in the oven.
[00:07:51.880 --> 00:07:54.880]   Hmm.
[00:07:54.880 --> 00:07:57.880]   I'm knocked out.
[00:07:57.880 --> 00:07:59.880]   I'm not sure what you're doing.
[00:07:59.880 --> 00:08:01.880]   I'm not sure what you're doing.
[00:08:01.880 --> 00:08:03.880]   I'm not sure what you're doing.
[00:08:03.880 --> 00:08:05.880]   I'm not sure what you're doing.
[00:08:05.880 --> 00:08:07.880]   I'm not sure what you're doing.
[00:08:07.880 --> 00:08:09.880]   I'm not sure what you're doing.
[00:08:09.880 --> 00:08:11.880]   I'm not sure what you're doing.
[00:08:11.880 --> 00:08:13.880]   I'm not sure what you're doing.
[00:08:13.880 --> 00:08:15.880]   I'm not sure what you're doing.
[00:08:15.880 --> 00:08:17.880]   I'm not sure what you're doing.
[00:08:17.880 --> 00:08:19.880]   I'm not sure what you're doing.
[00:08:19.880 --> 00:08:21.880]   I'm not sure what you're doing.
[00:08:21.880 --> 00:08:23.880]   I'm not sure what you're doing.
[00:08:23.880 --> 00:08:25.880]   I'm not sure what you're doing.
[00:08:25.880 --> 00:08:28.880]   That's hardly a prompt.
[00:08:28.880 --> 00:08:30.880]   But you're right.
[00:08:30.880 --> 00:08:35.880]   What is your young man do for a living?
[00:08:35.880 --> 00:08:39.880]   He owns a used record store here in El Paso.
[00:08:39.880 --> 00:08:41.880]   Music lover, right?
[00:08:41.880 --> 00:08:44.880]   He's fond of music.
[00:08:44.880 --> 00:08:46.880]   Not me all.
[00:08:46.880 --> 00:08:54.880]   And what are you doing for a J.O.B. these days?
[00:08:55.880 --> 00:08:58.880]   I work in the record store.
[00:08:58.880 --> 00:09:06.880]   Oh, so it all suddenly seems so clear.
[00:09:06.880 --> 00:09:09.880]   Do you like it?
[00:09:09.880 --> 00:09:13.880]   Yeah, I like it a lot, smartass.
[00:09:13.880 --> 00:09:15.880]   I get to listen to music all day.
[00:09:15.880 --> 00:09:17.880]   Talk about music all day.
[00:09:17.880 --> 00:09:20.880]   It's really cool.
[00:09:20.880 --> 00:09:22.880]   It's going to be a great environment
[00:09:22.880 --> 00:09:27.880]   for a little girl to grow up in.
[00:09:27.880 --> 00:09:30.880]   As opposed to getting around the world,
[00:09:30.880 --> 00:09:33.880]   killing human beings, and being paid best
[00:09:33.880 --> 00:09:36.880]   sums of money.
[00:09:36.880 --> 00:09:38.880]   Precisely.
[00:09:38.880 --> 00:09:41.880]   Well, my own friend.
[00:09:41.880 --> 00:09:43.880]   Do we choose someone?
[00:09:43.880 --> 00:09:48.880]   However, all cocklockery aside,
[00:09:48.880 --> 00:09:51.880]   I am looking forward to meeting your young man.
[00:09:51.880 --> 00:09:54.880]   I happen to be more or less particular.
[00:09:54.880 --> 00:09:59.880]   Who might get married?
[00:09:59.880 --> 00:10:01.880]   You want to come to the wedding?
[00:10:01.880 --> 00:10:04.880]   Only if I can sit on the bright side.
[00:10:04.880 --> 00:10:07.880]   You'll find it a bit lonely on my side.
[00:10:07.880 --> 00:10:11.880]   Your side always was a bit lonely.
[00:10:11.880 --> 00:10:15.880]   But I wouldn't sit anywhere else.
[00:10:15.880 --> 00:10:20.880]   You know, I had a lovely stream of money.
[00:10:20.880 --> 00:10:22.880]   Lovely stream about you.
[00:10:22.880 --> 00:10:23.880]   Oh, here's Tommy.
[00:10:23.880 --> 00:10:25.880]   Call me, Arlene.
[00:10:25.880 --> 00:10:26.880]   You must be Tommy.
[00:10:26.880 --> 00:10:27.880]   Uh-huh.
[00:10:27.880 --> 00:10:29.880]   Arlene's told me so much about you.
[00:10:29.880 --> 00:10:30.880]   Aren't you okay?
[00:10:30.880 --> 00:10:31.880]   Oh, I'm fine.
[00:10:31.880 --> 00:10:34.880]   Tommy, I'd like you to meet my father.
[00:10:34.880 --> 00:10:37.880]   Oh, my God.
[00:10:37.880 --> 00:10:39.880]   Oh, my God, this is great.
[00:10:39.880 --> 00:10:41.880]   I'm so glad to meet you, sir.
[00:10:41.880 --> 00:10:42.880]   Oh, Dad.
[00:10:42.880 --> 00:10:44.880]   The name is Bill.
[00:10:44.880 --> 00:10:46.880]   Well, it's great to meet you.
[00:10:46.880 --> 00:10:47.880]   Bill.
[00:10:47.880 --> 00:10:49.880]   Arlene told me you could make it.
[00:10:49.880 --> 00:10:50.880]   Surprise.
[00:10:50.880 --> 00:10:52.880]   That's my pop for you.
[00:10:52.880 --> 00:10:54.880]   Always full of surprises.
[00:10:54.880 --> 00:11:00.880]   Well, in the surprise department, the apple doesn't fall far from the tree.
[00:11:00.880 --> 00:11:02.880]   When did you get in?
[00:11:02.880 --> 00:11:03.880]   Just now.
[00:11:03.880 --> 00:11:05.880]   Did you come straight from Australia?
[00:11:05.880 --> 00:11:06.880]   Of course.
[00:11:06.880 --> 00:11:08.880]   Daddy, I told Tommy that you were in Perth,
[00:11:08.880 --> 00:11:11.880]   lining for silver and no one could meet you.
[00:11:11.880 --> 00:11:15.880]   Lucky for us all, that's not the case.
[00:11:15.880 --> 00:11:19.880]   So, what's this all about?
[00:11:19.880 --> 00:11:26.880]   I've heard of wedding rehearsals, but I don't believe I've ever heard of a wedding dress rehearsal before.
[00:11:26.880 --> 00:11:33.880]   We thought, well, I paid so much money for a dress you only going to wear once, especially when Arlene looks so goddamn beautiful in it.
[00:11:33.880 --> 00:11:38.880]   So, uh, we're going to try to get all the mileage we can out of it.
[00:11:38.880 --> 00:11:43.880]   Isn't it supposed to be bad luck for the groom to see the bride and her wedding dress?
[00:11:43.880 --> 00:11:45.880]   People with a ceremony?
[00:11:45.880 --> 00:11:50.880]   Well, I guess I just believe I'm having dangerous.
[00:11:50.880 --> 00:11:53.880]   I know just what you mean.
[00:11:53.880 --> 00:11:54.880]   Some.
[00:11:54.880 --> 00:11:56.880]   Some of us are places to be.
[00:11:56.880 --> 00:11:58.880]   Show them to do.
[00:11:58.880 --> 00:12:01.880]   Look, we got to go through this one more time.
[00:12:01.880 --> 00:12:03.880]   So, uh, why don't you have a--
[00:12:03.880 --> 00:12:05.880]   Oh, my God.
[00:12:05.880 --> 00:12:06.880]   What am I thinking?
[00:12:06.880 --> 00:12:07.880]   You should give her away.
[00:12:07.880 --> 00:12:10.880]   Tommy, that's not exactly Daddy's cup of tea.
[00:12:10.880 --> 00:12:15.880]   I'm not even sure if you're much more comfortable sitting with the rest of the cats.
[00:12:15.880 --> 00:12:17.880]   Really?
[00:12:17.880 --> 00:12:20.880]   That's asking a lot.
[00:12:20.880 --> 00:12:21.880]   No.
[00:12:21.880 --> 00:12:22.880]   Okay.
[00:12:22.880 --> 00:12:23.880]   Forget it.
[00:12:23.880 --> 00:12:25.880]   But how about we go out to dinner tonight, celebrate?
[00:12:25.880 --> 00:12:28.880]   Only on the condition that I pay for everything.
[00:12:28.880 --> 00:12:29.880]   Deal.
[00:12:29.880 --> 00:12:31.880]   We have to do this now.
[00:12:31.880 --> 00:12:32.880]   Can I watch?
[00:12:32.880 --> 00:12:33.880]   Absolutely.
[00:12:33.880 --> 00:12:35.880]   Have a seat.
[00:12:35.880 --> 00:12:37.880]   Which is the bride's side.
[00:12:37.880 --> 00:12:39.880]   Right over here.
[00:12:39.880 --> 00:12:44.880]   Mother, here we go.
[00:12:44.880 --> 00:12:45.880]   Yes.
[00:12:45.880 --> 00:12:48.880]   Now, son, pop them, bowels.
[00:12:48.880 --> 00:12:49.880]   Yeah.
[00:12:49.880 --> 00:12:51.880]   You can't hear me.
[00:12:51.880 --> 00:12:53.880]   You should be.
[00:12:53.880 --> 00:12:54.880]   No.
[00:12:54.880 --> 00:12:58.880]   I just don't want to.
[00:12:58.880 --> 00:13:00.880]   You don't want me to put them there.
[00:13:00.880 --> 00:13:07.880]   If he's the man you want, then go stand by.
[00:13:07.880 --> 00:13:31.880]   [MUSIC]
[00:13:31.880 --> 00:13:33.880]   Does it look pretty?
[00:13:33.880 --> 00:13:35.880]   Oh, yeah.
[00:13:35.880 --> 00:13:45.880]   [MUSIC]
[00:13:45.880 --> 00:13:47.880]   Thank you.
[00:13:47.880 --> 00:13:52.880]   [MUSIC]
[00:13:52.880 --> 00:13:59.880]   [MUSIC]
```

## ggml-base.en.bin

Some stats:

```
whisper_model_load: mem required  =  310.00 MB (+    6.00 MB per decoder)
whisper_model_load: model size    =  140.54 MB

whisper_print_timings:    total time = 433205.62 ms

```

**So time needed was ~ 433 seconds**

Actual transcription:

```
[00:00:00.000 --> 00:00:15.000]   [Music]
[00:00:15.000 --> 00:00:17.000]   Do you find me sadistic?
[00:00:17.000 --> 00:00:20.000]   No, Kato.
[00:00:20.000 --> 00:00:23.000]   I'd like to believe
[00:00:23.000 --> 00:00:27.000]   you're aware enough, even now.
[00:00:27.000 --> 00:00:33.000]   I know that there is nothing sadistic in my actions.
[00:00:33.000 --> 00:00:36.000]   This moment,
[00:00:36.000 --> 00:00:40.000]   this is me,
[00:00:40.000 --> 00:00:44.000]   and I most miss the case.
[00:00:44.000 --> 00:00:45.000]   Well,
[00:00:45.000 --> 00:00:48.000]   it's your baby.
[00:00:48.000 --> 00:00:54.000]   The dead didn't I?
[00:00:55.000 --> 00:00:57.000]   Well, I wasn't.
[00:00:57.000 --> 00:01:00.000]   But it wasn't from lack of try and I can tell you that.
[00:01:00.000 --> 00:01:03.000]   Actually, Bill's last bullet put me in a coma.
[00:01:03.000 --> 00:01:07.000]   A coma I was to lie in for four years.
[00:01:07.000 --> 00:01:09.000]   When I woke up,
[00:01:09.000 --> 00:01:15.000]   I went on with the movie advertisements referred to as a roaring rampage of revenge.
[00:01:15.000 --> 00:01:17.000]   I roared,
[00:01:17.000 --> 00:01:19.000]   and I rampaged,
[00:01:19.000 --> 00:01:22.000]   and I got bloody satisfaction.
[00:01:22.000 --> 00:01:26.000]   I've killed a hell of a lot of people who get to this point.
[00:01:26.000 --> 00:01:29.000]   But I have only one more.
[00:01:29.000 --> 00:01:31.000]   The last one.
[00:01:31.000 --> 00:01:35.000]   The one I'm driving to right now.
[00:01:35.000 --> 00:01:38.000]   The only one left.
[00:01:38.000 --> 00:01:41.000]   And when I arrive at my destination,
[00:01:41.000 --> 00:01:45.000]   I am gonna kill Bill.
[00:01:45.000 --> 00:02:02.000]   [Music]
[00:02:02.000 --> 00:02:14.000]   Now the incident that happened at the two pines wedding chapel
[00:02:14.000 --> 00:02:20.000]   that put this whole gory story into motion has since become legend.
[00:02:20.000 --> 00:02:23.000]   Massacre at two pines.
[00:02:23.000 --> 00:02:25.000]   That's what the newspapers called it.
[00:02:25.000 --> 00:02:31.000]   The local TV news called it the El Paso Texas Wedding Chapel Massacre.
[00:02:31.000 --> 00:02:32.000]   How it happened?
[00:02:32.000 --> 00:02:33.000]   Who was there?
[00:02:33.000 --> 00:02:36.000]   How many got killed and who killed them?
[00:02:36.000 --> 00:02:40.000]   Changes depending on who's telling the story.
[00:02:40.000 --> 00:02:42.000]   In actual fact,
[00:02:42.000 --> 00:02:46.000]   the massacre didn't happen during a wedding at all.
[00:02:46.000 --> 00:02:48.000]   It was a wedding rehearsal.
[00:02:48.000 --> 00:02:53.000]   Now when we come to the park where I say you may kiss the bride,
[00:02:53.000 --> 00:02:55.000]   you may kiss the bride.
[00:02:55.000 --> 00:02:59.000]   But don't stick your tongue in her mouth.
[00:02:59.000 --> 00:03:02.000]   This might be funny to your friends,
[00:03:02.000 --> 00:03:06.000]   but it would be embarrassing to your parents.
[00:03:06.000 --> 00:03:11.000]   We'll try to be strange.
[00:03:11.000 --> 00:03:16.000]   Y'all got a song?
[00:03:16.000 --> 00:03:18.000]   How about "Love Me Tender"?
[00:03:18.000 --> 00:03:22.000]   I can play that.
[00:03:22.000 --> 00:03:24.000]   Let me tend to be great.
[00:03:24.000 --> 00:03:27.000]   Rufus, he's the man.
[00:03:27.000 --> 00:03:28.000]   Rufus?
[00:03:28.000 --> 00:03:30.000]   Who was that to use to play for?
[00:03:30.000 --> 00:03:32.000]   Rufus Thomas.
[00:03:32.000 --> 00:03:34.000]   Rufus Thomas.
[00:03:34.000 --> 00:03:36.000]   Rufus Thomas.
[00:03:36.000 --> 00:03:37.000]   I was a drill.
[00:03:37.000 --> 00:03:38.000]   I was a drifted.
[00:03:38.000 --> 00:03:40.000]   I was a coaster.
[00:03:40.000 --> 00:03:42.000]   I was part of the gang.
[00:03:42.000 --> 00:03:44.000]   I was a bar-k.
[00:03:44.000 --> 00:03:48.000]   If they come through Texas, I'd play with him.
[00:03:48.000 --> 00:03:50.000]   Rufus?
[00:03:50.000 --> 00:03:54.000]   He's the man.
[00:03:54.000 --> 00:03:57.000]   Have I forgot anything?
[00:03:57.000 --> 00:04:00.000]   Oh yes, you forgot the seating arrangements.
[00:04:00.000 --> 00:04:03.000]   Thank you, mother.
[00:04:03.000 --> 00:04:05.000]   Now the way we normally do this,
[00:04:05.000 --> 00:04:08.000]   we have the bride's side,
[00:04:08.000 --> 00:04:12.000]   but since the bride ain't got nobody coming,
[00:04:12.000 --> 00:04:16.000]   and the groom's got far too many people coming,
[00:04:16.000 --> 00:04:20.000]   well yeah, they're coming all the way from Oklahoma.
[00:04:20.000 --> 00:04:22.000]   Right.
[00:04:22.000 --> 00:04:27.000]   Well, I don't see no problem with the groom's side
[00:04:27.000 --> 00:04:29.000]   sharing the bride's side.
[00:04:29.000 --> 00:04:30.000]   Do you, mother?
[00:04:30.000 --> 00:04:32.000]   Not a problem with that,
[00:04:32.000 --> 00:04:37.000]   but honey, you know, it would be good if you had somebody come
[00:04:37.000 --> 00:04:41.000]   You know, is it sign of good faith?
[00:04:41.000 --> 00:04:44.000]   Well, I don't have anybody,
[00:04:44.000 --> 00:04:48.000]   except for Tommy and my friends.
[00:04:48.000 --> 00:04:51.000]   You have no family?
[00:04:51.000 --> 00:04:53.000]   Well, I'm working on changing then.
[00:04:53.000 --> 00:04:55.000]   Mrs. Harmony, we're all the family
[00:04:55.000 --> 00:04:58.000]   this Alangel's ever going to need.
[00:04:58.000 --> 00:05:00.000]   I'm not feeling very well,
[00:05:00.000 --> 00:05:03.000]   and this bitch is starting to piss me off.
[00:05:03.000 --> 00:05:05.000]   So while you all bother on,
[00:05:05.000 --> 00:05:08.000]   I'm going to go outside and get some air.
[00:05:08.000 --> 00:05:10.000]   I'm sorry.
[00:05:10.000 --> 00:05:12.000]   She's going to go out and get some air.
[00:05:12.000 --> 00:05:14.000]   Yeah, given her delicate condition,
[00:05:14.000 --> 00:05:17.000]   she just needs a few minutes to give it to get us to be okay.
[00:05:18.000 --> 00:05:21.000]   [music]
[00:05:22.000 --> 00:05:25.000]   [music]
[00:05:26.000 --> 00:05:29.000]   [music]
[00:05:30.000 --> 00:05:33.000]   [music]
[00:05:34.000 --> 00:05:37.000]   [music]
[00:05:38.000 --> 00:05:41.000]   [music]
[00:05:42.000 --> 00:05:45.000]   [music]
[00:05:46.000 --> 00:05:49.000]   [music]
[00:05:50.000 --> 00:05:53.000]   [music]
[00:05:53.000 --> 00:05:57.000]   [music]
[00:05:57.000 --> 00:06:01.000]   [music]
[00:06:01.000 --> 00:06:05.000]   [music]
[00:06:05.000 --> 00:06:09.000]   [music]
[00:06:09.000 --> 00:06:13.000]   [music]
[00:06:36.000 --> 00:06:40.000]   Hello, kiddo.
[00:06:40.000 --> 00:06:46.000]   How did you find me?
[00:06:46.000 --> 00:06:50.000]   I'm the man.
[00:06:50.000 --> 00:06:54.000]   What are you doing here?
[00:06:54.000 --> 00:06:58.000]   What am I doing?
[00:06:58.000 --> 00:07:00.000]   Well,
[00:07:00.000 --> 00:07:06.000]   I was playing my flute.
[00:07:06.000 --> 00:07:12.000]   At this moment,
[00:07:12.000 --> 00:07:15.000]   I'm looking at the most beautiful bride
[00:07:15.000 --> 00:07:19.000]   in these old eyes of every scene.
[00:07:19.000 --> 00:07:21.000]   Why are you here?
[00:07:21.000 --> 00:07:25.000]   Last look.
[00:07:25.000 --> 00:07:27.000]   Are you going to be nice?
[00:07:27.000 --> 00:07:31.000]   I've never been nice my whole life.
[00:07:31.000 --> 00:07:36.000]   But I'll do my best to be sweet.
[00:07:36.000 --> 00:07:39.000]   I always told you,
[00:07:39.000 --> 00:07:42.000]   your sweet side is your best side.
[00:07:42.000 --> 00:07:49.000]   I guess that's why you're the only one who's ever seen it.
[00:07:49.000 --> 00:07:54.000]   See, you got a bun in the oven?
[00:07:54.000 --> 00:07:58.000]   I'm knocked up.
[00:07:58.000 --> 00:08:00.000]   Chase Louise.
[00:08:00.000 --> 00:08:02.000]   That young man here is sure
[00:08:02.000 --> 00:08:06.000]   it doesn't believe in wasting time, does he?
[00:08:06.000 --> 00:08:10.000]   Have you seen Tommy?
[00:08:10.000 --> 00:08:12.000]   A guy on the tux?
[00:08:12.000 --> 00:08:13.000]   Yes.
[00:08:13.000 --> 00:08:16.000]   And I saw him.
[00:08:16.000 --> 00:08:20.000]   I like his hair.
[00:08:20.000 --> 00:08:24.000]   You promised you'd be nice.
[00:08:24.000 --> 00:08:26.000]   I said I'd do my best.
[00:08:26.000 --> 00:08:29.000]   That's hardly a promise.
[00:08:29.000 --> 00:08:31.000]   But you're right.
[00:08:31.000 --> 00:08:36.000]   What does your young man do for a living?
[00:08:36.000 --> 00:08:40.000]   He owns a used record store here in El Paso.
[00:08:40.000 --> 00:08:42.000]   He's a lover, right?
[00:08:42.000 --> 00:08:45.000]   He's fond of music.
[00:08:45.000 --> 00:08:51.000]   Aren't we all?
[00:08:51.000 --> 00:08:56.000]   And what are you doing for a J.O.B. these days?
[00:08:56.000 --> 00:08:59.000]   I work in the record store.
[00:08:59.000 --> 00:09:03.000]   Ah, so...
[00:09:03.000 --> 00:09:08.000]   it all suddenly seems so clear.
[00:09:08.000 --> 00:09:10.000]   Do you like it?
[00:09:10.000 --> 00:09:14.000]   Yeah, I like it a lot, smart ass.
[00:09:14.000 --> 00:09:17.000]   I get to listen to music all day.
[00:09:17.000 --> 00:09:21.000]   Talk about music all day. It's really cool.
[00:09:21.000 --> 00:09:28.000]   It's going to be a great environment for my little girl to grow up in.
[00:09:28.000 --> 00:09:33.000]   As opposed to jetting around the world, killing human beams,
[00:09:33.000 --> 00:09:38.000]   and being paid best sums of money.
[00:09:38.000 --> 00:09:40.000]   Precisely.
[00:09:40.000 --> 00:09:44.000]   I have a friend.
[00:09:44.000 --> 00:09:47.000]   Do each you own.
[00:09:47.000 --> 00:09:51.000]   However, all clockwork re-assigned.
[00:09:51.000 --> 00:09:55.000]   I am looking forward to meeting your young man.
[00:09:55.000 --> 00:09:59.000]   I happen to be more or less particular.
[00:09:59.000 --> 00:10:03.000]   Oh, my God, Mary.
[00:10:03.000 --> 00:10:05.000]   You want to come to the wedding?
[00:10:05.000 --> 00:10:08.000]   Only if I can sit on the bride's side.
[00:10:08.000 --> 00:10:12.000]   Your side always was a bit lonely.
[00:10:12.000 --> 00:10:17.000]   But I wouldn't sit anywhere else.
[00:10:17.000 --> 00:10:22.000]   You know, I had a lovely stream about you.
[00:10:22.000 --> 00:10:25.000]   Oh, here's Tommy. Call me Arlene.
[00:10:25.000 --> 00:10:29.000]   You must be Tommy. Arlene's told me so much about you.
[00:10:29.000 --> 00:10:31.000]   Are you okay?
[00:10:31.000 --> 00:10:35.000]   Oh, I'm fine. Tommy, I'd like you to meet my father.
[00:10:35.000 --> 00:10:38.000]   Oh, my God.
[00:10:38.000 --> 00:10:40.000]   Oh, my God, this is great.
[00:10:40.000 --> 00:10:42.000]   I'm so glad to meet you, sir.
[00:10:42.000 --> 00:10:45.000]   Oh, Dad, the name is Bill.
[00:10:45.000 --> 00:10:48.000]   Well, it's great to meet you. Bill.
[00:10:48.000 --> 00:10:50.000]   Arlene told me you could make it.
[00:10:50.000 --> 00:10:51.000]   Surprise.
[00:10:51.000 --> 00:10:54.000]   That's my pot for you. Always full of surprises.
[00:10:54.000 --> 00:10:58.000]   Well, in a surprise department.
[00:10:58.000 --> 00:11:01.000]   The Apple doesn't fall far from the tree.
[00:11:01.000 --> 00:11:04.000]   When did you get in? Just now.
[00:11:04.000 --> 00:11:06.000]   Did you come straight from Australia?
[00:11:06.000 --> 00:11:07.000]   Of course.
[00:11:07.000 --> 00:11:09.000]   Daddy, I told Tommy that you were in Perth,
[00:11:09.000 --> 00:11:13.000]   finding for silver, and no one could reach you.
[00:11:13.000 --> 00:11:16.000]   Lucky for us all, that's not the case.
[00:11:16.000 --> 00:11:20.000]   So, what's this all about?
[00:11:20.000 --> 00:11:27.000]   I've heard of wedding rehearsals, but I don't believe I've ever heard of a wedding dress rehearsal before.
[00:11:27.000 --> 00:11:31.000]   We thought, "Why pay so much money for a dress you only gonna wear once?"
[00:11:31.000 --> 00:11:34.000]   Especially when Arlene looks so goddamn beautiful in it.
[00:11:34.000 --> 00:11:39.000]   So, we're gonna try to get all the mileage we can out of it.
[00:11:39.000 --> 00:11:44.000]   Isn't it supposed to be bad luck for the groom to see the bride in her wedding dress?
[00:11:44.000 --> 00:11:46.000]   People with a ceremony?
[00:11:46.000 --> 00:11:51.000]   Wow. I guess I just believe in them dangerously.
[00:11:51.000 --> 00:11:54.000]   I know just what you mean.
[00:11:54.000 --> 00:11:59.000]   "San, Sama Lacha, places to be. It's your duty."
[00:11:59.000 --> 00:12:02.000]   But we gotta go through this one more time.
[00:12:02.000 --> 00:12:05.000]   So, uh, why don't you have a... oh my god.
[00:12:05.000 --> 00:12:08.000]   What am I thinking? You should give her away!
[00:12:08.000 --> 00:12:11.000]   Tommy, that's not exactly Daddy's cup of tea.
[00:12:11.000 --> 00:12:16.000]   I think Father seemed much more comfortable sitting with the rest of the guests.
[00:12:16.000 --> 00:12:18.000]   Really?
[00:12:18.000 --> 00:12:21.000]   That's asking a lot.
[00:12:21.000 --> 00:12:24.000]   Oh. Okay. We'll forget it.
[00:12:24.000 --> 00:12:26.000]   But how about we go out to dinner tonight and celebrate?
[00:12:26.000 --> 00:12:29.000]   Only on the condition that I pay for everything.
[00:12:29.000 --> 00:12:32.000]   Deal. We have to do this now.
[00:12:32.000 --> 00:12:33.000]   Can I watch?
[00:12:33.000 --> 00:12:36.000]   Absolutely. You have a seat.
[00:12:36.000 --> 00:12:38.000]   Which is the bride's side?
[00:12:38.000 --> 00:12:40.000]   Right over here.
[00:12:40.000 --> 00:12:45.000]   Father, here we go.
[00:12:45.000 --> 00:12:50.000]   Yeah. Now, Sean, drop them bows.
[00:12:50.000 --> 00:12:53.000]   Yeah.
[00:12:53.000 --> 00:12:56.000]   Oh, Sean.
[00:12:56.000 --> 00:12:59.000]   Oh. I just want...
[00:12:59.000 --> 00:13:03.000]   You don't want me a damn thing.
[00:13:03.000 --> 00:13:08.000]   If he's the man you want, then go stand by.
[00:13:08.000 --> 00:13:11.000]   [Sighs]
[00:13:11.000 --> 00:13:34.000]   Does it look pretty?
[00:13:34.000 --> 00:13:37.000]   Oh, yes.
[00:13:37.000 --> 00:13:40.000]   [Sighs]
[00:13:40.000 --> 00:13:49.000]   Thank you.
[00:13:49.000 --> 00:13:56.000]   [Sighs]
[00:13:56.000 --> 00:14:00.000]   [Music]
```


## ggml-small.en.bin

Some stats:


```
whisper_model_load: mem required  =  743.00 MB (+   16.00 MB per decoder)
whisper_model_load: model size    = 464.44 MB

whisper_print_timings:    total time = 1713762.12 ms
```

**So time needed was ~ 1713 seconds (almost half an hour)**

And the actual transcription:

```
[00:00:00.000 --> 00:00:10.000]   [MUSIC]
[00:00:10.000 --> 00:00:17.000]   Do you find me sadistic?
[00:00:17.000 --> 00:00:21.000]   No, kiddo.
[00:00:21.000 --> 00:00:27.000]   I'd like to believe you're aware enough, even now,
[00:00:27.000 --> 00:00:33.000]   to know that there is nothing sadistic in my actions.
[00:00:33.000 --> 00:00:44.000]   This moment, this is me and my most nicer kiss to be.
[00:00:44.000 --> 00:00:48.000]   Well, it's your baby.
[00:00:48.000 --> 00:00:55.000]   Look, Dad, didn't I?
[00:00:55.000 --> 00:01:00.000]   Well, I wasn't. But it wasn't from lack of trying, I can tell you that.
[00:01:00.000 --> 00:01:03.000]   Actually, Bill's last bullet put me in a coma.
[00:01:03.000 --> 00:01:07.000]   A coma I was to lie in for four years.
[00:01:07.000 --> 00:01:11.000]   When I woke up, I went on with the movie advertisements
[00:01:11.000 --> 00:01:15.000]   referred to as a roaring rampage of revenge.
[00:01:15.000 --> 00:01:22.000]   I roared, and I rampaged, and I got bloody satisfaction.
[00:01:22.000 --> 00:01:26.000]   I've killed a hell of a lot of people to get to this point.
[00:01:26.000 --> 00:01:29.000]   But I have only one more.
[00:01:29.000 --> 00:01:31.000]   The last one.
[00:01:31.000 --> 00:01:35.000]   The one I'm driving to right now.
[00:01:35.000 --> 00:01:38.000]   The only one left.
[00:01:38.000 --> 00:01:45.000]   And when I arrive at my destination, I am gonna kill Bill.
[00:01:45.000 --> 00:02:10.000]   [Music]
[00:02:10.000 --> 00:02:14.000]   Now, the incident that happened at the Two Pines Wedding Chapel
[00:02:14.000 --> 00:02:20.000]   that put this whole gory story into motion has since become legend.
[00:02:20.000 --> 00:02:22.000]   Massacre at Two Pines.
[00:02:22.000 --> 00:02:24.000]   That's what the newspapers called it.
[00:02:24.000 --> 00:02:30.000]   The local TV news called it the El Paso, Texas Wedding Chapel Massacre.
[00:02:30.000 --> 00:02:36.000]   How it happened, who was there, how many got killed, and who killed them.
[00:02:36.000 --> 00:02:40.000]   Changes depending on who's telling the story.
[00:02:40.000 --> 00:02:45.000]   In actual fact, the massacre didn't happen during a wedding at all.
[00:02:45.000 --> 00:02:48.000]   It was a wedding rehearsal.
[00:02:48.000 --> 00:02:53.000]   Now, when we come to the park where I say you may kiss the bride,
[00:02:53.000 --> 00:02:55.000]   you may kiss the bride.
[00:02:55.000 --> 00:02:59.000]   But don't stick your tongue in her mouth.
[00:02:59.000 --> 00:03:06.000]   This might be funny to your friends, but it would be embarrassing to your parents.
[00:03:06.000 --> 00:03:10.000]   We'll try and restrain ourselves from that.
[00:03:10.000 --> 00:03:16.000]   Y'all got a song?
[00:03:16.000 --> 00:03:19.000]   How about "Love Me, Tender"? I can play that.
[00:03:19.000 --> 00:03:21.000]   Sure.
[00:03:21.000 --> 00:03:24.000]   "Love Me, Tender" would be great.
[00:03:24.000 --> 00:03:27.000]   Rufus, he's the man.
[00:03:27.000 --> 00:03:30.000]   Rufus, who was that you used to play for?
[00:03:30.000 --> 00:03:32.000]   Rufus Thomas.
[00:03:32.000 --> 00:03:34.000]   Rufus Thomas.
[00:03:34.000 --> 00:03:35.000]   Rufus Thomas.
[00:03:35.000 --> 00:03:39.000]   I was a drill, I was a drifter, I was a coaster,
[00:03:39.000 --> 00:03:43.000]   I was part of the gang, I was a bar-k.
[00:03:43.000 --> 00:03:47.000]   If they come through Texas, I haven't played with them.
[00:03:47.000 --> 00:03:53.000]   Rufus, he's the man.
[00:03:53.000 --> 00:03:56.000]   Have you forgotten anything?
[00:03:56.000 --> 00:04:00.000]   Oh, yes, you forgot the seating arrangements.
[00:04:00.000 --> 00:04:02.000]   Thank you, Mother.
[00:04:02.000 --> 00:04:07.000]   Now, the way we normally do this, we have the bride's side,
[00:04:07.000 --> 00:04:09.000]   and then we have the groom's side.
[00:04:09.000 --> 00:04:12.000]   But since the bride ain't got nobody coming,
[00:04:12.000 --> 00:04:16.000]   and the groom's got far too many people coming...
[00:04:16.000 --> 00:04:19.000]   Well, yeah, they're coming all the way from Oklahoma.
[00:04:19.000 --> 00:04:22.000]   Right.
[00:04:22.000 --> 00:04:29.000]   Well, I don't see no problem with the groom's side sharing the bride's side.
[00:04:29.000 --> 00:04:30.000]   Do you, Mother?
[00:04:30.000 --> 00:04:32.000]   I don't have a problem with that.
[00:04:32.000 --> 00:04:38.000]   But, honey, you know, it would be good if you had somebody come.
[00:04:38.000 --> 00:04:41.000]   You know, is that a sign of good faith?
[00:04:41.000 --> 00:04:48.000]   Well, I don't have anybody, except for Tommy and my friends.
[00:04:48.000 --> 00:04:51.000]   You have no family?
[00:04:51.000 --> 00:04:53.000]   Well, I'm working on changing that.
[00:04:53.000 --> 00:04:57.000]   Mrs. Harmony, we're all the family this little angel's ever gonna need.
[00:04:57.000 --> 00:05:03.000]   I'm not feeling very well, and this bitch is starting to piss me off.
[00:05:03.000 --> 00:05:07.000]   So while you all blather on, I'm gonna go outside and get some air.
[00:05:07.000 --> 00:05:09.000]   Um, uh, Reverend, sorry.
[00:05:09.000 --> 00:05:11.000]   She's gonna go out and get some air.
[00:05:11.000 --> 00:05:13.000]   Yeah, given her delicate condition.
[00:05:13.000 --> 00:05:16.000]   She just needs a few minutes to get it together. She'll be okay.
[00:05:16.000 --> 00:05:18.000]   Okay.
[00:05:19.000 --> 00:05:22.000]   [♪♪♪]
[00:05:23.000 --> 00:05:25.000]   [♪♪♪]
[00:05:26.000 --> 00:05:28.000]   [♪♪♪]
[00:05:28.000 --> 00:05:30.000]   [♪♪♪]
[00:05:30.000 --> 00:05:32.000]   [♪♪♪]
[00:05:33.000 --> 00:05:35.000]   [♪♪♪]
[00:05:36.000 --> 00:05:38.000]   [♪♪♪]
[00:05:39.000 --> 00:05:41.000]   [♪♪♪]
[00:05:41.000 --> 00:05:43.000]   [♪♪♪]
[00:05:43.000 --> 00:05:45.000]   [♪♪♪]
[00:05:45.000 --> 00:05:47.000]   [♪♪♪]
[00:05:47.000 --> 00:05:49.000]   [♪♪♪]
[00:05:49.000 --> 00:05:51.000]   [♪♪♪]
[00:05:51.000 --> 00:05:53.000]   [♪♪♪]
[00:05:53.000 --> 00:05:55.000]   [♪♪♪]
[00:05:55.000 --> 00:05:57.000]   [♪♪♪]
[00:05:57.000 --> 00:05:59.000]   [♪♪♪]
[00:05:59.000 --> 00:06:01.000]   [♪♪♪]
[00:06:01.000 --> 00:06:03.000]   [♪♪♪]
[00:06:03.000 --> 00:06:05.000]   [♪♪♪]
[00:06:05.000 --> 00:06:07.000]   [♪♪♪]
[00:06:07.000 --> 00:06:09.000]   [♪♪♪]
[00:06:36.000 --> 00:06:38.000]   Hello, kiddo.
[00:06:38.000 --> 00:06:45.000]   How did you find me?
[00:06:45.000 --> 00:06:48.000]   I'm the man.
[00:06:48.000 --> 00:06:53.000]   What are you doing here?
[00:06:53.000 --> 00:06:57.000]   What am I doing?
[00:06:57.000 --> 00:07:03.000]   Well, a moment ago I was playing my flute.
[00:07:04.000 --> 00:07:06.000]   [♪♪♪]
[00:07:06.000 --> 00:07:15.000]   At this moment, I'm looking at the most beautiful bride
[00:07:15.000 --> 00:07:18.000]   these old eyes have ever seen.
[00:07:18.000 --> 00:07:22.000]   Why are you here?
[00:07:22.000 --> 00:07:25.000]   Last look.
[00:07:25.000 --> 00:07:28.000]   Are you gonna be nice?
[00:07:28.000 --> 00:07:30.000]   I've never been nice my whole life.
[00:07:32.000 --> 00:07:34.000]   I'm just a guest to be sweet.
[00:07:34.000 --> 00:07:42.000]   I always told you, your sweet side is your best side.
[00:07:42.000 --> 00:07:47.000]   I guess that's why you're the only one who's ever seen it.
[00:07:47.000 --> 00:07:52.000]   See, you got a bun in the oven.
[00:07:52.000 --> 00:07:57.000]   I'm knocked up.
[00:07:58.000 --> 00:08:01.000]   I'm not a man of the way.
[00:08:01.000 --> 00:08:04.000]   I'm not a man of the way.
[00:08:04.000 --> 00:08:07.000]   I'm not a man of the way.
[00:08:07.000 --> 00:08:10.000]   I'm not a man of the way.
[00:08:10.000 --> 00:08:13.000]   I'm not a man of the way.
[00:08:13.000 --> 00:08:16.000]   I'm not a man of the way.
[00:08:16.000 --> 00:08:19.000]   I'm not a man of the way.
[00:08:19.000 --> 00:08:22.000]   I'm not a man of the way.
[00:08:22.000 --> 00:08:25.000]   I'm not a man of the way.
[00:08:26.000 --> 00:08:28.000]   It's hardly a promise.
[00:08:28.000 --> 00:08:31.000]   But you're right.
[00:08:31.000 --> 00:08:34.000]   What does your young man do for a living?
[00:08:34.000 --> 00:08:39.000]   He owns a used record store here in El Paso.
[00:08:39.000 --> 00:08:42.000]   A music lover, right?
[00:08:42.000 --> 00:08:44.000]   He's fond of music.
[00:08:44.000 --> 00:08:47.000]   Aren't we all?
[00:08:47.000 --> 00:08:55.000]   And what are you doing for a J-O-B these days?
[00:08:56.000 --> 00:08:58.000]   I work in the record store.
[00:08:58.000 --> 00:09:01.000]   Ah, so...
[00:09:01.000 --> 00:09:06.000]   it all suddenly seems so clear.
[00:09:06.000 --> 00:09:10.000]   Do you like it?
[00:09:10.000 --> 00:09:13.000]   Yeah, I like it a lot, smartass.
[00:09:13.000 --> 00:09:16.000]   I get to listen to music all day,
[00:09:16.000 --> 00:09:19.000]   talk about music all day. It's really cool.
[00:09:19.000 --> 00:09:24.000]   It's gonna be a great environment for my little girl to grow up in.
[00:09:24.000 --> 00:09:30.000]   As opposed to jetting around the world,
[00:09:30.000 --> 00:09:32.000]   killing human beings,
[00:09:32.000 --> 00:09:35.000]   and being paid vast sums of money.
[00:09:35.000 --> 00:09:39.000]   Precisely.
[00:09:39.000 --> 00:09:41.000]   Well, my old friend,
[00:09:41.000 --> 00:09:43.000]   to each his own.
[00:09:43.000 --> 00:09:45.000]   However,
[00:09:45.000 --> 00:09:49.000]   all cock-blockery aside,
[00:09:49.000 --> 00:09:52.000]   I am looking forward to meeting your young man.
[00:09:52.000 --> 00:09:55.000]   I happen to be more or less particular
[00:09:55.000 --> 00:09:58.000]   who my gal marries.
[00:09:58.000 --> 00:10:02.000]   You wanna come to the wedding?
[00:10:02.000 --> 00:10:04.000]   Only if I can sit on the bride's side.
[00:10:04.000 --> 00:10:08.000]   You'll find it a bit lonely on my side.
[00:10:08.000 --> 00:10:12.000]   Your side always was a bit lonely,
[00:10:12.000 --> 00:10:15.000]   but I wouldn't sit anywhere else.
[00:10:15.000 --> 00:10:19.000]   You know,
[00:10:19.000 --> 00:10:22.000]   I had the loveliest dream about you.
[00:10:22.000 --> 00:10:24.000]   Oh, here's Tommy. Call me Arlene.
[00:10:24.000 --> 00:10:27.000]   You must be Tommy.
[00:10:27.000 --> 00:10:29.000]   Arlene's told me so much about you.
[00:10:29.000 --> 00:10:31.000]   Honey, you okay?
[00:10:31.000 --> 00:10:32.000]   Oh, I'm fine.
[00:10:32.000 --> 00:10:35.000]   Tommy, I'd like you to meet my father.
[00:10:35.000 --> 00:10:38.000]   Oh, my God.
[00:10:38.000 --> 00:10:40.000]   Oh, my God, this is great.
[00:10:40.000 --> 00:10:42.000]   I'm so glad to meet you, sir.
[00:10:42.000 --> 00:10:43.000]   Oh, Dad.
[00:10:43.000 --> 00:10:45.000]   The name's Bill.
[00:10:45.000 --> 00:10:47.000]   Well, it's great to meet you.
[00:10:47.000 --> 00:10:50.000]   So, Arlene told me you couldn't make it.
[00:10:50.000 --> 00:10:51.000]   Surprise.
[00:10:51.000 --> 00:10:53.000]   That's my pot for you.
[00:10:53.000 --> 00:10:55.000]   Always full of surprises.
[00:10:55.000 --> 00:10:58.000]   Well, in the surprise department,
[00:10:58.000 --> 00:11:01.000]   the apple doesn't fall far from the tree.
[00:11:01.000 --> 00:11:03.000]   When did you get in?
[00:11:03.000 --> 00:11:04.000]   Just now.
[00:11:04.000 --> 00:11:06.000]   Did you come straight from Australia?
[00:11:06.000 --> 00:11:07.000]   Of course.
[00:11:07.000 --> 00:11:09.000]   Daddy, I told Tommy that you were in Perth
[00:11:09.000 --> 00:11:12.000]   lining for Silver and no one could reach you.
[00:11:12.000 --> 00:11:16.000]   Lucky for us all, that's not the case.
[00:11:16.000 --> 00:11:20.000]   So, what's this all about?
[00:11:20.000 --> 00:11:22.000]   I've heard of wedding rehearsals,
[00:11:22.000 --> 00:11:24.000]   but I don't believe I've ever heard
[00:11:24.000 --> 00:11:26.000]   of a wedding dress rehearsal before.
[00:11:26.000 --> 00:11:29.000]   We thought, why pay so much money for a dress
[00:11:29.000 --> 00:11:31.000]   you're only gonna wear once?
[00:11:31.000 --> 00:11:34.000]   Especially when Arlene looks so goddamn beautiful in it.
[00:11:34.000 --> 00:11:38.000]   So, I think we're gonna try to get all the mileage we can out of it.
[00:11:38.000 --> 00:11:41.000]   Isn't it supposed to be bad luck
[00:11:41.000 --> 00:11:44.000]   for the groom to see the bride in her wedding dress?
[00:11:44.000 --> 00:11:46.000]   People of the ceremony?
[00:11:46.000 --> 00:11:50.000]   I guess I just believe in living dangerously.
[00:11:50.000 --> 00:11:54.000]   I know just what you mean.
[00:11:54.000 --> 00:11:57.000]   Some...some of us are places to be.
[00:11:57.000 --> 00:11:59.000]   It's your duty.
[00:11:59.000 --> 00:12:01.000]   Look, we gotta go through this one more time.
[00:12:01.000 --> 00:12:03.000]   So, why don't you have a s...
[00:12:03.000 --> 00:12:05.000]   Oh, my God.
[00:12:05.000 --> 00:12:07.000]   What am I thinking? You should give her away.
[00:12:07.000 --> 00:12:11.000]   Tommy, that's not exactly Daddy's cup of tea.
[00:12:11.000 --> 00:12:14.000]   I think Father would be much more comfortable
[00:12:14.000 --> 00:12:16.000]   sitting with the rest of the guests.
[00:12:16.000 --> 00:12:18.000]   Really?
[00:12:18.000 --> 00:12:20.000]   That's asking a lot.
[00:12:20.000 --> 00:12:24.000]   Oh. Okay. We'll forget it.
[00:12:24.000 --> 00:12:26.000]   But how about we go out to dinner tonight and celebrate?
[00:12:26.000 --> 00:12:29.000]   Only on the condition that I pay for everything.
[00:12:29.000 --> 00:12:32.000]   Deal. We gotta do this now.
[00:12:32.000 --> 00:12:33.000]   Can I watch?
[00:12:33.000 --> 00:12:35.000]   Absolutely. Have a seat.
[00:12:35.000 --> 00:12:38.000]   Which is the bride's side?
[00:12:38.000 --> 00:12:40.000]   Right over here.
[00:12:41.000 --> 00:12:44.000]   Father, here we go.
[00:12:44.000 --> 00:12:45.000]   Yes.
[00:12:45.000 --> 00:12:48.000]   Now, son, about them vows.
[00:12:48.000 --> 00:12:57.000]   Belle.
[00:12:57.000 --> 00:12:58.000]   I just don't want...
[00:12:58.000 --> 00:13:01.000]   You know only a damn thing.
[00:13:01.000 --> 00:13:04.000]   If he's the man you want,
[00:13:04.000 --> 00:13:07.000]   then go stand by.
[00:13:07.000 --> 00:13:09.000]   Stand by.
[00:13:09.000 --> 00:13:33.000]   Do I look pretty?
[00:13:33.000 --> 00:13:35.000]   Oh, yes.
[00:13:35.000 --> 00:13:37.000]   Thank you.
[00:13:38.000 --> 00:13:40.000]   Thank you.
[00:13:41.000 --> 00:13:43.000]   Thank you.
[00:13:44.000 --> 00:13:46.000]   Thank you.
[00:13:47.000 --> 00:13:49.000]   Thank you.
[00:13:49.000 --> 00:13:52.000]   [♪♪♪]
[00:13:53.000 --> 00:13:55.000]   [♪♪♪]
[00:13:55.000 --> 00:13:57.420]   (soft music)
[00:13:57.420 --> 00:13:59.320]   (slow, dramatic music)

```


## ggml-medium.en.bin

Some stats:


```
whisper_model_load: mem required  = 1899.00 MB (+   43.00 MB per decoder)
whisper_model_load: model size    = 1462.12 MB

whisper_print_timings:    total time = 3563774.75 ms
```

**So time needed was ~ 3563 seconds (almost 1 hour)**

And the actual transcription:

```
[00:00:00.000 --> 00:00:15.000]   [Music]
[00:00:15.000 --> 00:00:19.000]   Do you find me sadistic?
[00:00:19.000 --> 00:00:21.000]   No, kiddo.
[00:00:21.000 --> 00:00:24.000]   I'd like to believe
[00:00:24.000 --> 00:00:27.000]   you're aware enough, even now,
[00:00:27.000 --> 00:00:31.000]   to know that there's nothing sadistic
[00:00:31.000 --> 00:00:34.000]   in my actions.
[00:00:34.000 --> 00:00:38.000]   This moment,
[00:00:38.000 --> 00:00:41.000]   this is me
[00:00:41.000 --> 00:00:44.000]   and my most masochistic.
[00:00:44.000 --> 00:00:46.000]   Well,
[00:00:46.000 --> 00:00:48.000]   it's your baby.
[00:00:48.000 --> 00:00:50.000]   [Gunshot]
[00:00:50.000 --> 00:00:53.000]   [Music]
[00:00:53.000 --> 00:00:55.000]   You looked dead, didn't I?
[00:00:55.000 --> 00:00:57.000]   Well, I wasn't.
[00:00:57.000 --> 00:01:00.000]   But it wasn't from lack of trying, I can tell you that.
[00:01:00.000 --> 00:01:03.000]   Actually, Bill's last bullet put me in a coma.
[00:01:03.000 --> 00:01:07.000]   A coma I was to lie in for four years.
[00:01:07.000 --> 00:01:09.000]   When I woke up,
[00:01:09.000 --> 00:01:15.000]   I went on what the movie advertisements refer to as a "roaring rampage of revenge."
[00:01:15.000 --> 00:01:18.000]   I roared, and I rampaged,
[00:01:18.000 --> 00:01:22.000]   and I got bloody satisfaction.
[00:01:22.000 --> 00:01:26.000]   I've killed a hell of a lot of people to get to this point.
[00:01:26.000 --> 00:01:29.000]   But I have only one more.
[00:01:29.000 --> 00:01:31.000]   The last one.
[00:01:31.000 --> 00:01:35.000]   The one I'm driving to right now.
[00:01:35.000 --> 00:01:38.000]   The only one left.
[00:01:38.000 --> 00:01:42.000]   And when I arrive at my destination,
[00:01:42.000 --> 00:01:45.000]   I am gonna kill Bill.
[00:01:45.000 --> 00:02:10.000]   [Music]
[00:02:10.000 --> 00:02:17.000]   Now, the incident that happened at the Two Pines wedding chapel that put this whole gory story into motion
[00:02:17.000 --> 00:02:20.000]   has since become legend.
[00:02:20.000 --> 00:02:22.000]   "Massacre at Two Pines."
[00:02:22.000 --> 00:02:24.000]   That's what the newspapers called it.
[00:02:24.000 --> 00:02:30.000]   The local TV news called it the "El Paso, Texas Wedding Chapel Massacre."
[00:02:30.000 --> 00:02:32.000]   How it happened.
[00:02:32.000 --> 00:02:33.000]   Who was there.
[00:02:33.000 --> 00:02:36.000]   How many got killed and who killed them.
[00:02:36.000 --> 00:02:40.000]   Changes depending on who's telling the story.
[00:02:40.000 --> 00:02:45.000]   In actual fact, the massacre didn't happen during a wedding at all.
[00:02:45.000 --> 00:02:48.000]   It was a wedding rehearsal.
[00:02:48.000 --> 00:02:55.000]   Now, when we come to the part where I say, "You may kiss the bride, you may kiss the bride,
[00:02:55.000 --> 00:02:59.000]   but don't stick your tongue in her mouth."
[00:02:59.000 --> 00:03:06.000]   This might be funny to your friends, but it would be embarrassing to your parents.
[00:03:06.000 --> 00:03:11.000]   We'll try to restrain ourselves from it.
[00:03:11.000 --> 00:03:16.000]   Y'all got a song?
[00:03:16.000 --> 00:03:20.000]   How about "Love Me Tender." I can play that.
[00:03:20.000 --> 00:03:22.000]   Sure.
[00:03:22.000 --> 00:03:24.000]   "Love Me Tender" would be great.
[00:03:24.000 --> 00:03:27.000]   Rufus, he's the man.
[00:03:27.000 --> 00:03:30.000]   Rufus, who was that you used to play for?
[00:03:30.000 --> 00:03:32.000]   Rufus Thomas.
[00:03:32.000 --> 00:03:35.000]   Rufus Thomas. Rufus Thomas.
[00:03:35.000 --> 00:03:43.000]   I was a drill, I was a drifter, I was a coaster, I was part of the gang, I was a bar-quet.
[00:03:43.000 --> 00:03:47.000]   If they come through Texas, I done played with them.
[00:03:47.000 --> 00:03:51.000]   Rufus, he's the man.
[00:03:54.000 --> 00:03:57.000]   Have you ever forgotten anything?
[00:03:57.000 --> 00:04:00.000]   Oh yes, you forgot the seating arrangements.
[00:04:00.000 --> 00:04:03.000]   Thank you, Mother.
[00:04:03.000 --> 00:04:10.000]   Now, the way we normally do this, we have the bride's side and then we have the groom's side.
[00:04:10.000 --> 00:04:17.000]   But since the bride ain't got nobody coming, and the groom's got far too many people coming.
[00:04:17.000 --> 00:04:21.000]   Well yeah, they're coming all the way from Oklahoma.
[00:04:21.000 --> 00:04:30.000]   Right. Well I don't see no problem with the groom's side sharing the bride's side. Do you, Mother?
[00:04:30.000 --> 00:04:32.000]   No, I don't have a problem with that.
[00:04:32.000 --> 00:04:38.000]   But, honey, you know it would be good if you had somebody come.
[00:04:38.000 --> 00:04:42.000]   You know, is it a sign of good faith?
[00:04:42.000 --> 00:04:49.000]   Well, I don't have anybody. Except for Tommy and my friends.
[00:04:49.000 --> 00:04:52.000]   You have no family?
[00:04:52.000 --> 00:04:54.000]   Well, I'm working on changing that.
[00:04:54.000 --> 00:04:58.000]   Mrs. Harmony, we're all the family this little angel's ever gonna need.
[00:04:58.000 --> 00:05:04.000]   I'm not feeling very well, and this bitch is starting to piss me off.
[00:05:04.000 --> 00:05:08.000]   So while you all blather on, I'm gonna go outside and get some air.
[00:05:08.000 --> 00:05:10.000]   Um, uh, Reverend, sorry.
[00:05:10.000 --> 00:05:12.000]   She's gonna go out and get some air?
[00:05:12.000 --> 00:05:14.000]   Yeah, given her delicate condition.
[00:05:14.000 --> 00:05:19.000]   She just needs a few minutes to get it together. She'll be okay.
[00:05:20.000 --> 00:05:25.000]   [Music]
[00:05:26.000 --> 00:05:31.000]   [Music]
[00:05:31.000 --> 00:05:36.000]   [Music]
[00:05:36.000 --> 00:05:41.000]   [Music]
[00:05:41.000 --> 00:05:46.000]   [Music]
[00:05:46.000 --> 00:05:51.000]   [Music]
[00:05:51.000 --> 00:05:56.000]   [Music]
[00:05:56.000 --> 00:06:01.000]   [Music]
[00:06:01.000 --> 00:06:06.000]   [Music]
[00:06:06.000 --> 00:06:11.000]   [Music]
[00:06:11.000 --> 00:06:16.000]   [Music]
[00:06:16.000 --> 00:06:21.000]   [Music]
[00:06:21.000 --> 00:06:26.000]   [Music]
[00:06:26.000 --> 00:06:31.000]   [Music]
[00:06:31.000 --> 00:06:36.000]   [Music]
[00:06:36.000 --> 00:06:38.000]   Hello, kiddo.
[00:06:38.000 --> 00:06:45.000]   How did you find me?
[00:06:45.000 --> 00:06:48.000]   I'm the man.
[00:06:48.000 --> 00:06:53.000]   What are you doing here?
[00:06:55.000 --> 00:06:57.000]   What am I doing?
[00:06:57.000 --> 00:07:03.000]   Well, a moment ago I was playing my flute.
[00:07:03.000 --> 00:07:17.000]   This moment, I'm looking at the most beautiful bride these whole eyes have ever seen.
[00:07:17.000 --> 00:07:21.000]   Why are you here?
[00:07:21.000 --> 00:07:23.000]   Last look.
[00:07:24.000 --> 00:07:26.000]   Are you gonna be nice?
[00:07:26.000 --> 00:07:29.000]   I've never been nice my whole life.
[00:07:29.000 --> 00:07:34.000]   But I'll do my best to be sweet.
[00:07:34.000 --> 00:07:41.000]   I always told you, your sweet side is your best side.
[00:07:41.000 --> 00:07:46.000]   I guess that's why you're the only one who's ever seen it.
[00:07:46.000 --> 00:07:51.000]   See, you got a bun in the oven.
[00:07:52.000 --> 00:07:53.000]   Hmm.
[00:07:53.000 --> 00:07:56.000]   I'm knocked up.
[00:07:56.000 --> 00:07:59.000]   Jeez, Louise.
[00:07:59.000 --> 00:08:04.000]   That young man of yours sure doesn't believe in wasting time, does he?
[00:08:04.000 --> 00:08:07.000]   Have you seen Tommy?
[00:08:07.000 --> 00:08:11.000]   Big guy in the tux?
[00:08:11.000 --> 00:08:12.000]   Yes.
[00:08:12.000 --> 00:08:14.000]   Then I saw him.
[00:08:14.000 --> 00:08:18.000]   I like his hair.
[00:08:20.000 --> 00:08:22.000]   You promised you'd be nice.
[00:08:22.000 --> 00:08:28.000]   I said I'd do my best. That's hardly a promise.
[00:08:28.000 --> 00:08:30.000]   But you're right.
[00:08:30.000 --> 00:08:34.000]   What does your young man do for a living?
[00:08:34.000 --> 00:08:39.000]   He owns a used record store here in El Paso.
[00:08:39.000 --> 00:08:41.000]   Ah. Music lover, eh?
[00:08:41.000 --> 00:08:44.000]   He's fond of music.
[00:08:44.000 --> 00:08:47.000]   Aren't we all?
[00:08:48.000 --> 00:08:52.000]   And what are you doing for a J.O.B. these days?
[00:08:52.000 --> 00:08:55.000]   I work in the record store.
[00:08:55.000 --> 00:08:59.000]   Ah, so...
[00:08:59.000 --> 00:09:03.000]   it all suddenly seems so clear.
[00:09:03.000 --> 00:09:07.000]   Do you like it?
[00:09:07.000 --> 00:09:10.000]   Yeah, I like it a lot, smartass.
[00:09:10.000 --> 00:09:13.000]   I get to listen to music all day.
[00:09:14.000 --> 00:09:17.000]   Talk about music all day. It's really cool.
[00:09:17.000 --> 00:09:22.000]   It's gonna be a great environment for my little girl to grow up in.
[00:09:22.000 --> 00:09:30.000]   As opposed to jetting around the world, killing human beings,
[00:09:30.000 --> 00:09:33.000]   and being paid vast sums of money?
[00:09:33.000 --> 00:09:36.000]   Precisely.
[00:09:36.000 --> 00:09:39.000]   Well, my old friend,
[00:09:39.000 --> 00:09:41.000]   to each his own,
[00:09:42.000 --> 00:09:44.000]   to each his own.
[00:09:44.000 --> 00:09:49.000]   However, all cock-luckery aside,
[00:09:49.000 --> 00:09:52.000]   I am looking forward to meeting your young man.
[00:09:52.000 --> 00:09:56.000]   I happen to be more or less particular,
[00:09:56.000 --> 00:09:58.000]   whom my gout marries.
[00:09:58.000 --> 00:10:02.000]   You wanna come to the wedding?
[00:10:02.000 --> 00:10:05.000]   Only if I can sit on the bride's side.
[00:10:05.000 --> 00:10:09.000]   You'll find it a bit lonely on my side.
[00:10:09.000 --> 00:10:12.000]   Your side always was a bit lonely.
[00:10:12.000 --> 00:10:15.000]   But I wouldn't sit anywhere else.
[00:10:15.000 --> 00:10:19.000]   You know,
[00:10:19.000 --> 00:10:22.000]   I had the loveliest dream about you.
[00:10:22.000 --> 00:10:25.000]   Oh, here's Tommy. Call me Arlene.
[00:10:25.000 --> 00:10:27.000]   You must be Tommy.
[00:10:27.000 --> 00:10:29.000]   Arlene's told me so much about you.
[00:10:29.000 --> 00:10:31.000]   Arlene, you okay?
[00:10:31.000 --> 00:10:32.000]   Oh, I'm fine.
[00:10:32.000 --> 00:10:35.000]   Tommy, I'd like you to meet my father.
[00:10:35.000 --> 00:10:38.000]   Oh, my God!
[00:10:38.000 --> 00:10:40.000]   Oh, my God! This is great!
[00:10:40.000 --> 00:10:42.000]   I'm so glad to meet you, sir.
[00:10:42.000 --> 00:10:43.000]   Oh, Dad.
[00:10:43.000 --> 00:10:45.000]   The name's Bill.
[00:10:45.000 --> 00:10:47.000]   Well, it's great to meet you, Bill.
[00:10:47.000 --> 00:10:49.000]   Arlene told me you couldn't make it.
[00:10:49.000 --> 00:10:51.000]   Surprise.
[00:10:51.000 --> 00:10:52.000]   That's my pop for you.
[00:10:52.000 --> 00:10:54.000]   Always full of surprises.
[00:10:54.000 --> 00:10:57.000]   Well, in the surprise department,
[00:10:57.000 --> 00:11:00.000]   the apple doesn't fall far from the tree.
[00:11:00.000 --> 00:11:02.000]   When did you get in?
[00:11:02.000 --> 00:11:03.000]   Just now.
[00:11:03.000 --> 00:11:05.000]   Did you come straight from Australia?
[00:11:05.000 --> 00:11:07.000]   Of course.
[00:11:07.000 --> 00:11:09.000]   Daddy, I told Tommy that you were in Perth
[00:11:09.000 --> 00:11:12.000]   mining for silver, and no one could reach you.
[00:11:12.000 --> 00:11:16.000]   Lucky for us all, that's not the case.
[00:11:16.000 --> 00:11:20.000]   So, what's this all about?
[00:11:20.000 --> 00:11:22.000]   I've heard of wedding rehearsals,
[00:11:22.000 --> 00:11:24.000]   but I don't believe I've ever heard
[00:11:24.000 --> 00:11:27.000]   of a wedding dress rehearsal before.
[00:11:27.000 --> 00:11:28.000]   We thought,
[00:11:28.000 --> 00:11:29.000]   "Why pay so much money for a dress
[00:11:29.000 --> 00:11:31.000]   you're only gonna wear once?"
[00:11:31.000 --> 00:11:34.000]   Especially when Arlene looks so goddamn beautiful in it.
[00:11:34.000 --> 00:11:36.000]   So, uh, I think we're gonna try to get all the mileage
[00:11:36.000 --> 00:11:37.000]   we can out of it.
[00:11:37.000 --> 00:11:41.000]   Isn't it supposed to be bad luck
[00:11:41.000 --> 00:11:44.000]   for the groom to see the bride in her wedding dress
[00:11:44.000 --> 00:11:46.000]   before the ceremony?
[00:11:46.000 --> 00:11:50.000]   Well, I guess I just believe I live in danger, so...
[00:11:50.000 --> 00:11:54.000]   I know just what you mean.
[00:11:54.000 --> 00:11:57.000]   Son, some of us have places to be.
[00:11:57.000 --> 00:11:59.000]   It's your old dude.
[00:11:59.000 --> 00:12:01.000]   Look, we gotta go through this one more time.
[00:12:01.000 --> 00:12:03.000]   So, uh, why don't you have a s--
[00:12:03.000 --> 00:12:05.000]   Oh, my God.
[00:12:05.000 --> 00:12:07.000]   What am I thinking? You should give her away.
[00:12:07.000 --> 00:12:11.000]   Tommy, that's not exactly Daddy's cup of tea.
[00:12:11.000 --> 00:12:14.000]   I think Father would be much more comfortable
[00:12:14.000 --> 00:12:16.000]   sitting with the rest of the guests.
[00:12:16.000 --> 00:12:17.000]   Really?
[00:12:17.000 --> 00:12:19.000]   That's asking a lot.
[00:12:19.000 --> 00:12:21.000]   Oh.
[00:12:21.000 --> 00:12:23.000]   Okay. Well, forget it.
[00:12:23.000 --> 00:12:26.000]   But how about we go out to dinner tonight and celebrate?
[00:12:26.000 --> 00:12:29.000]   Only on the condition that I pay for everything.
[00:12:29.000 --> 00:12:31.000]   Deal. We gotta do this now.
[00:12:31.000 --> 00:12:33.000]   Can I watch?
[00:12:33.000 --> 00:12:35.000]   Absolutely. Have a seat.
[00:12:35.000 --> 00:12:37.000]   Which is the bride's side?
[00:12:37.000 --> 00:12:39.000]   Right over here.
[00:12:39.000 --> 00:12:44.000]   Mother, here we go.
[00:12:44.000 --> 00:12:49.000]   Now, son, about them vows.
[00:12:49.000 --> 00:12:57.000]   No.
[00:12:57.000 --> 00:12:59.000]   I just don't want...
[00:12:59.000 --> 00:13:02.000]   You don't owe me a damn thing.
[00:13:03.000 --> 00:13:05.000]   If he's the man you want,
[00:13:05.000 --> 00:13:08.000]   then go stand by.
[00:13:08.000 --> 00:13:10.000]   [chuckles]
[00:13:10.000 --> 00:13:34.000]   Do I look pretty?
[00:13:34.000 --> 00:13:36.000]   Oh, yeah.
[00:13:36.000 --> 00:13:39.000]   [♪♪♪]
[00:13:39.000 --> 00:13:48.000]   Thank you.
[00:13:48.000 --> 00:13:51.000]   [♪♪♪]
[00:13:51.000 --> 00:13:54.000]   [♪♪♪]
[00:13:54.000 --> 00:13:57.000]   [♪♪♪]
[00:13:57.000 --> 00:13:59.920]   [MUSIC]
```

## Comparison of results


|	tiny 160 s	|	base 433 s	|	small 1713 s	|	medium	3563 s |
|	-----	|	--------|	--------|	-------- |
|	Do you finally sit just now?	|	Do you find me sadistic?	|	Do you find me sadistic?	|	Do you find me sadistic?	|
|	[MUSIC PLAYING]	|	No, Kato.	|	No, kiddo.	|	No, kiddo.	|
|	No, I can't do.	|	I'd like to believe	|	I'd like to believe you're aware enough, even now,	|	I'd like to believe	|
|	I'd like to believe you're aware enough even now.	|	you're aware enough, even now.	|	to know that there is nothing sadistic in my actions.	|	you're aware enough, even now,	|
|	No, that there is nothing suggesting in my actions.	|	I know that there is nothing sadistic in my actions.	|	This moment, this is me and my most nicer kiss to be.	|	to know that there's nothing sadistic	|
|	This moment, this is me and my most nice against them.	|	This moment,	|	Well, it's your baby.	|	in my actions.	|
|	Well, it's your name.	|	this is me,	|	Look, Dad, didn't I?	|	This moment,	|
|	[MUSIC PLAYING]	|	and I most miss the case.	|	Well, I wasn't. But it wasn't from lack of trying, I can tell you that.	|	this is me	|
|	But Dad didn't I?	|	Well,	|	Actually, Bill's last bullet put me in a coma.	|	and my most masochistic.	|
|	Well, I wasn't.	|	it's your baby.	|	A coma I was to lie in for four years.	|	Well,	|
|	But it wasn't from lack of trying.	|	The dead didn't I?	|	When I woke up, I went on with the movie advertisements	|	it's your baby.	|
|	I can tell you that.	|	Well, I wasn't.	|	referred to as a roaring rampage of revenge.	|	[Gunshot]	|
|	Actually, Bill's last bullet put me in a coma.	|	But it wasn't from lack of try and I can tell you that.	|	I roared, and I rampaged, and I got bloody satisfaction.	|	[Music]	|
|	A coma, I was to lie in for four years.	|	Actually, Bill's last bullet put me in a coma.	|	I've killed a hell of a lot of people to get to this point.	|	You looked dead, didn't I?	|
|	And I woke up.	|	A coma I was to lie in for four years.	|	But I have only one more.	|	Well, I wasn't.	|
|	I went on with a movie advertisements	|	When I woke up,	|	The last one.	|	But it wasn't from lack of trying, I can tell you that.	|
|	for two as a roaring rampage of revenge.	|	I went on with the movie advertisements referred to as a roaring rampage of 	|	The one I'm driving to right now.	|	Actually, Bill's last bullet put me in a coma.	|
|	I roared.	|	I roared,	|	The only one left.	|	A coma I was to lie in for four years.	|
|	And I relanged.	|	and I rampaged,	|	And when I arrive at my destination, I am gonna kill Bill.	|	When I woke up,	|
|	And I got bloody satisfaction.	|	and I got bloody satisfaction.	|		|	I went on what the movie advertisements refer to as a "roaring rampage of revenege."	|
|	I've killed a hell of a lot of people to get to this point.	|	I've killed a hell of a lot of people who get to this point.	|		|	I roared, and I rampaged,	|
|	But I have only one more.	|	But I have only one more.	|		|	and I got bloody satisfaction.	|
|	The last one.	|	The last one.	|		|	I've killed a hell of a lot of people to get to this point.	|
|	The one I'm driving to right now.	|	The one I'm driving to right now.	|		|	But I have only one more.	|
|	The only one left.	|	The only one left.	|		|	The last one.	|
|	And when I arrive at my destination,	|	And when I arrive at my destination,	|		|	The one I'm driving to right now.	|
|	I have going to kill Bill.	|	I am gonna kill Bill.	|		|	The only one left.	|
|		|		|		|	And when I arrive at my destination,	|
|		|		|		|	I am gonna kill Bill.	|


# Conclusion

If you take a peek at the above results (and you remember the movie or download an .srt of the actual subtitles) you'll see that the results for the small and medium model were almost perfect! The base model was also good enough considering that it took much less time than these two. 

The tiny model wasn't so good however even that model is good enough to understand everything that is being said in the movie from the subtitles and context. Finally, consider that both the tiny and base models were faster than real-time even on my (very slow) computer.

