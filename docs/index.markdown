---
layout: home
profile_picture:
  src: /assets/img/profile-pic.jpg
  alt: website picture
---
<p> This purpose of this project is to digitize and publish the sermons of my Dad, Kevin Brew. </p> 

<p> Dad's collection of sermons spanned from the late 70's until now. He had a bunch of sermons printed out on rolling printer paper which he has scanned in, some in .doc format and some in .docs. Also during COVID he gave his services online. </p>

<p> The <b>current</b> primary reason for this repository is to put all his sermons (or as many as he can find!) in one place, in a standard format. This is because he is planning to write a book and so having all the content in one place might enable a bit of human and machine analysis to see if there are common threads across his works that he might use as a foundation for his work </p>

<p> It might also be of interest to you, you might want to read his old sermons or it could be a good dataset for some NLP tasks such as topic analysis of sermons over time. Over time I will add some more content here based on what we find!

<p> The sermons have been processed as follows. Sermons in Dads collection were available in .doc and scanned .pdf formats.
<ol>
<li> The doc files were converted to PDF (so that the orginal content could be displayed on the site). Text was then extracted from the doc files. </li>
<li> The pdf files had optical character recognition applied to them. Google vision API provided the best results. </li>
<li> The files had a challenging format, no date was present, but hints to the date were there. Also (especially the OCR text files) had artifacts in them where the scan had failed. To remdedy this GPT was applied to
   <ul>
   <li> Clean the text, be correcting for well observed OCR issues (like l's being recognised as i's) </li>
   <li> Identify the date </li>
   <li> Create a short summary for the Sermon </li>
   </ul></li>
</ol>
