use promptly::prompt;
use std::error::Error;
use url::Url;

#[derive(Debug)]
pub struct ParsedAnswers {
    pub url: Url,
    pub manga_name: String,
    pub chapter_range: Vec<f32>,
}

pub fn parse_chapter(chapters: String) -> Result<Vec<f32>, Box<dyn Error>> {
    let mut parsed_chapters: Vec<f32> = vec![];

    let split_whitespace: Vec<&str> = chapters.split_whitespace().collect();
    for _str in split_whitespace {
        if _str.contains("..") {
            let nums = _str
                .split("..")
                .map(|s| s.parse::<i32>())
                .collect::<Result<Vec<i32>, _>>()?;

            if nums.len() != 2 {
                return Err(format!("More than 3 values in iterator: {}", _str).into());
            }

            if nums.first() > nums.last() {
                return Err(format!("Iterator values should be ascending: {}", _str).into());
            }
            let first = *nums.first().expect("Couldn't find first");
            let last = 1 + *nums.last().expect("Couldn't find last");
            parsed_chapters.append(&mut (first..last).map(|i| i as f32).collect());
        } else {
            parsed_chapters.push(_str.parse::<f32>()?)
        }
    }

    Ok(parsed_chapters)
}

pub fn prompt_user() -> ParsedAnswers {
    println!("Use '..' for ranges, and put a space in between each range or chapter");
    let url = loop {
        let user_input_url: String = match prompt("Link") {
            Ok(u) => u,
            Err(err) => {
                panic!("[ERROR] Couldn't Read URL: {}", err)
            }
        };
        let parsed_url = Url::parse(&user_input_url);
        match parsed_url {
            Ok(url) => {
                break url;
            }
            Err(err) => {
                println!("[ERROR] Couldn't Parse URL: {}", err);
                continue;
            }
        };
    };

    let chapter_range = loop {
        let chapter_range: String = match prompt("Chapters") {
            Ok(c) => c,
            Err(err) => {
                panic!("[ERROR] Couldn't Read Chapter Range: {}", err);
            }
        };
        match parse_chapter(chapter_range) {
            Ok(chapters) => {
                break chapters;
            }
            Err(err) => {
                println!("[ERROR] Couldn't Parse Chapters {:?}", err);
                continue;
            }
        };
    };

    let manga_name = loop {
        let _: String = match prompt("Manga Name") {
            Ok(m) => {
                break m;
            }
            Err(err) => {
                panic!("[ERROR] Couldn't Read Manga Name: {}", err);
            }
        };
    };

    ParsedAnswers {
        url,
        manga_name,
        chapter_range,
    }
}
