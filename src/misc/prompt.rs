use promptly::prompt;
use std::error::Error;
use url::Url;

struct PromptAnswers {
    url: String,
    manga_name: String,
    chapter_range: String,
}

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

fn prompt_user() -> Result<PromptAnswers, Box<dyn Error>> {
    println!("Use '..' for ranges, and put a space in between each range or chapter");

    let url: String = prompt("Link")?;
    let chapter_range: String = prompt("Chapters")?;
    let manga_name: String = prompt("Manga Name")?;

    Ok(PromptAnswers {
        url,
        manga_name,
        chapter_range,
    })
}

pub fn get_user_input() -> ParsedAnswers {
    let answers = match prompt_user() {
        Ok(answer) => answer,
        Err(err) => panic!("[ERROR] Couldn't Read Prompt {:?}", err),
    };

    let chapters = match parse_chapter(answers.chapter_range) {
        Ok(chapters) => chapters,
        Err(err) => panic!("[ERROR] Couldn't Parse Chapters {:?}", err),
    };

    let url = Url::parse(&answers.url);
    let url = match url {
        Ok(url) => url,
        Err(err) => panic!("[ERROR] Couldn't Parse URL: {}", err)
    };

    ParsedAnswers {
        url,
        manga_name: answers.manga_name,
        chapter_range: chapters
    }
}
