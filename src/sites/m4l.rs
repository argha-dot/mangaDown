use std::fs;
use std::io::{self, Write};
use std::sync::{Arc, Mutex};

use camino::Utf8Path;
use futures::{stream, StreamExt};
use reqwest::Client;
use url::Url;

use crate::misc::utils::{create_folder, download_page, is_int, zip_rename_delete};
use crate::misc::ParsedAnswers;

pub async fn get_multiple_chapters(answers: ParsedAnswers) {
    let client = Client::new();
    for chapter in answers.chapter_range {
        download_chapter(&answers.url, &answers.manga_name, chapter, &client).await;
    }

    println!("\n\t\tALL CHAPTERS DOWNLOAD");
}

pub async fn download_chapter(base_url: &Url, manga_name: &str, chapter: f32, client: &Client) {
    let loader = vec!["\\", "|", "/", "-"];
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

    let pages: Vec<i32> = (1..1001).collect();
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
    let shared_loader_coutnter = Arc::new(Mutex::new(1));

    stream::iter(pages)
        .map(|i| {
            let url_file_string = format!("{}-{:0>3}.png", url_chapter_string, i);
            let url = match base_url.join(&url_file_string) {
                Ok(url) => url,
                Err(err) => panic!("[ERROR] Can't Get url {:?}", err),
            };

            let client = client;
            let file_path = chapter_path.join(format!("{:0>3}.png", i));
            let s_continue = shared_continue.clone();
            let s_counter = shared_loader_coutnter.clone();
            let loader = loader.clone();

            async move {
                if *s_continue.lock().unwrap() {
                    match download_page(client, url.clone(), &file_path).await {
                        Ok(_) => {
                            let mut counter = s_counter.lock().unwrap();
                            print!("\x1b[K\x1b[1G");
                            print!("CHAPTER: {} [{}]", chapter, loader[*counter % loader.len()]);
                            io::stdout().flush().unwrap();

                            *counter += 1;
                        }
                        Err(_) => {
                            let mut state = s_continue.lock().unwrap();
                            *state = false;
                        }
                    }
                }
            }
        })
        .buffer_unordered(15)
        .collect::<Vec<()>>()
        .await;

    zip_rename_delete(&chapter_path, &chapter_folder_name);

    print!("\x1b[K\x1b[1G");
    if *shared_loader_coutnter.clone().lock().unwrap() == 1 {
        eprintln!("[ERROR] CHAPTER {} MAY NOT EXIST", chapter);
        // TODO: CLEANUP ON FAIL
        let zip_path = &chapter_path
            .parent()
            .unwrap()
            .join(format!("{}.zip", &chapter_folder_name));
        let _ = match fs::remove_file(zip_path) {
            Ok(_) => {},
            Err(_) => {},
        };
    } else {
        println!(
            "[CHAPTER {} DONE]: {}",
            chapter,
            *shared_loader_coutnter.clone().lock().unwrap()
        )
    }
}
