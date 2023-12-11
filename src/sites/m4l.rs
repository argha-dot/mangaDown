use std::sync::{Arc, Mutex};

use camino::Utf8Path;
use futures::{stream, StreamExt};
use reqwest::Client;
use url::Url;

use crate::misc::ParsedAnswers;
use crate::misc::utils::{create_folder, download_page, is_int, zip_rename_delete};

pub async fn get_multiple_chapters(answers: ParsedAnswers) {

    let client = Client::new();
    for chapter in answers.chapter_range {
        download_chapter(&answers.url, &answers.manga_name, chapter, &client).await;
    }

    println!("\nALL CHAPTERS DOWNLOAD");
}

pub async fn download_chapter(base_url: &Url, manga_name: &str, chapter: f32, client: &Client) {
    let (chapter_folder_name, is_point_chapter) = if is_int(chapter) {
        (format!("{} {}", manga_name, chapter.floor()), false)
    } else {
        (format!("{} {}", manga_name, chapter), true)
    };

    let chapter_path = Utf8Path::new("./")
        .join(&manga_name)
        .join(&chapter_folder_name);
    let _ = match create_folder(&chapter_path) {
        Ok(_) => {}
        Err(err) => panic!("[ERROR] Can't Create Folder {:?}", err),
    };

    let pages: Vec<i32> = (1..101).collect();

    let url_chapter_string = if is_point_chapter {
        println!(
            "{:0>4}.{}",
            chapter.trunc(),
            (chapter.fract() * 10.0).floor()
        );
        format!(
            "{:0>4}.{}",
            chapter.trunc(),
            (chapter.fract() * 10.0).floor()
        )
    } else {
        format!("{:0>4}", chapter)
    };

    let shared_continue = Arc::new(Mutex::new(true));

    stream::iter(pages)
        .map(|i| {
            let url_file_string = format!("{}-{:0>3}.png", url_chapter_string, i);
            let url = match base_url.join(&url_file_string) {
                Ok(url) => url,
                Err(err) => panic!("[ERROR] Can't Get url {:?}", err),
            };

            let client = client;
            let file_path = chapter_path.join(format!("{:0>3}.png", i));
            let s_continue = Arc::clone(&shared_continue);

            async move {
                if *s_continue.lock().unwrap() {
                    match download_page(client, url.clone(), &file_path).await {
                        Ok(_) => {}
                        Err(_) => {
                            let mut state = s_continue.lock().unwrap();
                            *state = false;
                            if i == 1 {
                                println!("CHAPTER MAY NOT EXIST");
                            } else {
                                println!("CHAPTER DOWNLOADED");
                            }
                        }
                    }
                }
            }
        })
        .buffer_unordered(5)
        .collect::<Vec<()>>()
        .await;

    zip_rename_delete(&chapter_path, &chapter_folder_name);
}
