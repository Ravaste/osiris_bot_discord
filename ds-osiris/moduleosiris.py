import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer, app_commands
from discord.ext import commands, tasks
import random
from datetime import *
import re
import os	
import openai
from openai import AsyncOpenAI
import requests
from dotenv import load_dotenv
import urllib.parse, urllib.request, re
import json
import asyncio
import yt_dlp
import urllib.parse, urllib.request, re
import difflib
from pathlib import Path
import gzip
import subprocess
import aiohttp
from icalendar import Calendar
from zoneinfo import ZoneInfo