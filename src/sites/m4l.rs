use camino::Utf8Path;
use reqwest::Client;
use url::Url;

use crate::utils::{create_folder, download_page, is_int, zip_rename_delete};

pub async fn download_chapter(base_url: &str, manga_name: &str, chapter: f32, client: &Client) {
    let (chapter_folder_name, is_point_chapter) = if is_int(chapter) {
        (format!("{} {}", manga_name, chapter.floor()), false)
    } else {
        (format!("{} {}", manga_name, chapter), true)
    };
    // println!("{} {}", chapter_folder_name, is_point_chapter);
    let chapter_path = Utf8Path::new("./")
        .join(&manga_name)
        .join(&chapter_folder_name);
    let _ = match create_folder(&chapter_path) {
        Ok(_) => {}
        Err(err) => panic!("[ERROR] Can't Create Folder {:?}", err),
    };

    let pages: Vec<i32> = (1..1001).collect();
    let base_url = Url::parse(&base_url);
    let base_url = match base_url {
        Ok(url) => url,
        Err(err) => panic!("[ERROR] Can't Get url {:?}", err),
    };

    let url_chapter_string = if is_point_chapter {
        println!("{:0>4}.{}", chapter.trunc(), (chapter.fract() * 10.0).floor());
        format!("{:0>4}.{}", chapter.trunc(), (chapter.fract() * 10.0).floor())
    } else {
        format!("{:0>4}", chapter)
    };

    for i in pages.iter() {
        let url_file_string = format!("{}-{:0>3}.png", url_chapter_string, i);
        let url = match base_url.join(&url_file_string) {
            Ok(url) => url,
            Err(err) => panic!("[ERROR] Can't Get url {:?}", err),
        };

        let client = client;
        let file_path = chapter_path.join(format!("{:0>3}.png", i));
        let _ = match download_page(client, url.clone(), &file_path).await {
            Ok(_) => {}
            Err(_) => {
                if *i == 1 {
                    println!("CHAPTER MAY NOT EXIST")
                } else {
                    println!("CHAPTER DOWNLOADED");
                    break;
                }
            }
        };

        println!("finished {}", i);
    }

    zip_rename_delete(&chapter_path, &chapter_folder_name);
}
