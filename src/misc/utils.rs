use std::fs;
use std::io::Write;
use std::{error::Error, fs::File};

use bytes::Bytes;
use camino::Utf8Path;
use reqwest::Client;
use url::Url;
use zip_extensions::zip_create_from_directory;

pub fn is_int(value: f32) -> bool {
    (value.fract() < 1e-6) || ((1.0 - value.fract()) < 1e-6)
}

pub fn create_folder(path: &Utf8Path) -> Result<(), Box<dyn Error>> {
    if !path.exists() {
        fs::create_dir_all(path)?;
    }
    Ok(())
}

pub fn write_file(file_path: &Utf8Path, file_content: Bytes) -> Result<(), Box<dyn Error>> {
    let mut file = File::create(file_path)?;
    file.write_all(file_content.as_ref())?;
    Ok(())
}

pub fn zip_rename_delete(chapter_path: &Utf8Path, chapter_folder_name: &str) {
    let zip_path = &chapter_path
        .parent()
        .unwrap()
        .join(format!("{}.zip", &chapter_folder_name));
    let cbz_path = &chapter_path
        .parent()
        .unwrap()
        .join(format!("{}.cbz", &chapter_folder_name));

    let _ = match zip_create_from_directory(
        &zip_path.as_std_path().to_path_buf(),
        &chapter_path.as_std_path().to_path_buf(),
    ) {
        Ok(()) => {}
        Err(err) => panic!("[ERROR] Couldn't create zip {:?}", err),
    };

    let _ = match fs::rename(zip_path, cbz_path) {
        Ok(()) => {}
        Err(err) => panic!("[ERROR] Couldn't rename zip {:?}", err),
    };

    let _ = match fs::remove_dir_all(chapter_path) {
        Ok(()) => {}
        Err(err) => panic!("[ERROR] Couldn't Delete Folder {:?}", err),
    };
}

pub async fn download_page(
    client: &Client,
    url: Url,
    file_path: &Utf8Path,
) -> Result<(), Box<dyn Error>> {
    let res = client.get(url).send().await?;
    let _ = match res.error_for_status_ref() {
        Ok(_) => {}
        Err(err) => return Err(Box::new(err)),
    };
    let file_content = res.bytes().await?;

    write_file(file_path, file_content)?;
    Ok(())
}
