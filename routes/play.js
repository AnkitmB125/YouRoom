const express = require('express'),
    router = express.Router(),
    { dbVideo } = require('../dbModels/video'),
    getSearchResults = require('../controllers/getSearchResults'),
    mongoose = require('mongoose')
const  spawn  = require('child_process').spawnSync;    

router.get('/:id', async (req, res, next) => {
    
    if(!req.user) {
         res.redirect('/index');
    }
    try {
        let video = await dbVideo.findOne({ _id: mongoose.Types.ObjectId(req.params.id) });
        
        if (!video) {
            res.status('404').send("Not a valid request");
        } else {
            let title = video.title;
            
            let videos = await getSearchResults(title);
            
            if(req.query.keyword) {
                
                const pyprog = spawn('python', ["/home/ankitb/Documents/visa/python/youtube_transcriber.py",  "/home/ankitb/Documents/visa/assets/"+videos[0].id+".mp4", "/home/ankitb/Documents/visa/assets/"+videos[0].id+".srt", req.query.keyword] );

                var keyword_seek = JSON.parse(pyprog.stdout.toString());
                
                res.render('play.ejs', { videos: videos, video: video, user: req.user, qs: req.query, keyword_seek: keyword_seek, keyword: req.query.keyword, detection_fast: null});
            } 
            else if (req.query.detection_fast) {
                console.log(req.query.detection_fast);
                
                const pyprog = spawn('python', ["/home/ankitb/Documents/visa/python/detection_fast.py",  "/home/ankitb/Documents/visa/assets/"+videos[0].id+".mp4", req.query.detection_fast] );

                var keyword_fast = JSON.parse(pyprog.stdout.toString());
                
                res.render('play.ejs', { videos: videos, video: video, user: req.user, qs: req.query, keyword_seek: null, keyword: null, detection_fast: keyword_fast});

            }
            else {   
                res.render('play.ejs', { videos: videos, video: video, user: req.user, qs: req.query, keyword_seek: null, keyword: null, detection_fast: null });
            }
        }
    } catch (err) {
        console.log(err);
        res.send(err);
    }
    // console.log(req.query);
    // res.send("hello");
});


module.exports = router;