import React, { useState, useEffect } from 'react';
import bridge from '@vkontakte/vk-bridge';
import {
	ConfigProvider,
	View,
	Panel,
	Button,
	PanelHeader,
	Placeholder,
	Input,
	ModalRoot,
	ModalCard,
	Snackbar,
	Avatar,
	Group,
	List,
	SimpleCell,
	Header,
	Search,
} from '@vkontakte/vkui';
import {
	Icon56CompassOutline,
	Icon16Cancel,
	Icon16Done,
	Icon24Dismiss,
} from '@vkontakte/icons';
import '@vkontakte/vkui/dist/vkui.css';

import ErrorBoundary from './ErrorBoundary';

import {
    authUser,
    getParse,
		addParse,
		deleteParse,
} from './Functions/api';
import './App.css';

const App = () => {
	const [userVk, setUserVk] = useState(null);
	const [user, setUser] = useState(null);
	const [scheme, setScheme] = useState('client_light');
	const [activeModal, setActiveModal] = useState(null);

	const [parseList, setParseList] = useState(null);
	const [inputAdd, setInputAdd] = useState('');
	const [search, setSearch] = useState('');

	const [posts, setPosts] = useState([]);
	const [popup, setPopup] = useState({
		current: null,
		text: null,
	});

	useEffect(() => {
		bridge.send('VKWebAppInit');
		bridge.subscribe(({ detail: { type, data }}) => {
			if (type === 'VKWebAppUpdateConfig') {
				if (data['appearance'] === 'dark') {
					setScheme('space_gray');
					bridge.send("VKWebAppSetViewSettings", {
						"status_bar_style": "light",
						"action_bar_color": "#19191a",
					}).catch(() => {});
				} else {
					setScheme('bright_light');
					bridge.send("VKWebAppSetViewSettings", {
						"status_bar_style": "dark",
						"action_bar_color": "#f4f5fb",
					}).catch(() => {});
				}
			}
		});
		async function fetchData() {
			const user = await bridge.sendPromise('VKWebAppGetUserInfo');
			const url = document.location.search;
			setUserVk(user);

			authUser({ url }, onPopup).then((e) => {
				if (e.status !== 'error') {
					setUser(e.result);
					setParseList(e.result.parse);
				} else if (e.type === 429) {
					setTimeout(() => {
						onPopup('429');
					}, 300);
				}
			});
		}
		fetchData();
	}, []);

	const onPopup = (current = null, text = null) => {
		setPopup({ current, text });
	};

	const onModal = (type = null) => {
		if (type) {
			document.body.style.overflow = 'hidden';
		} else {
			document.body.style.overflow = 'unset';
		}
		setActiveModal(type);
	};

	const onSearch = (current = null, text = null) => {
		setPopup({ current, text });
	};

	const modal = (
    <ModalRoot
			activeModal={activeModal}
		>
			<ModalCard
				id="add"
				onClose={() => {
					onModal();
				}}
				header="Подписаться на парсинг аккаунта"
				actions={[
					{
						title: 'Добавить',
						mode: 'primary',
						action: () => {
							addParse({
								text: inputAdd,
							}, onPopup).then((e) => {
								if (e.status !== 'error') {
									onPopup('success', 'Успешно');
								}
								onModal();
							});
							onModal();
						},
					},
				]}
			>
				<Input
					maxLength="100"
					value={inputAdd}
					placeholder="Введите аккаунт"
					onChange={(event) => { setInputAdd(event.target.value); }}
				/>
			</ModalCard>
    </ModalRoot>
  );

	return (
		<ErrorBoundary>
			<ConfigProvider scheme={scheme}>
				{(popup.current === 'success' || popup.current === 'error') && (
					<Snackbar
						layout="vertical"
						onClose={() => { onPopup(); }}
						before={
							<Avatar size={24} className="snackbar_avatar">
								{popup.current === 'error' ? (
									<Icon16Cancel fill="#fff" width={14} height={14} />
								) : (
									<Icon16Done fill="#fff" width={14} height={14} />
								)}
							</Avatar>
						}
					>
						{popup.text ? popup.text : ''}
					</Snackbar>
				)}
				{popup.current === '429' && (
					<div className="popup">
						<div className="popup_content">
							<div className="popup_title">Ошибка загрузки</div>
							<div className="popup_btn_block">
								<Button
									size="l"
									mode="primary"
									onClick={() => {
										document.location.reload();
										onPopup();
									}}
								>Обновить приложение</Button>
							</div>
						</div>
					</div>
				)}
				<View
					id="home"
					activePanel="home"
					modal={modal}
				>
					<Panel id="home">
						<PanelHeader>InstaParse</PanelHeader>
						{console.log(parseList)}
							{parseList === null ? (
								<Placeholder
			            icon={<Icon56CompassOutline />}
			            action={<Button size="l" mode="tertiary" onClick={() => { onModal('add'); }}>Добавить</Button>}
			            stretched
			          >
			            Нет аккаунтов для парсинга
			          </Placeholder>
							) : (
								<>
									<Group header={<Header mode="secondary">Активные аккаунты</Header>}>
		                <List>
		                  {parseList.map((item, index) => (
		                    <SimpleCell
													key={item.account}
													after={
														<Icon24Dismiss
															fill="var(--accent)"
															onClick={(e) => {
																deleteParse({
																	text: item.account,
																}, onPopup).then((e) => {
																	if (e.status !== 'error') {
																		onPopup('success', 'Успешно');

																		parseList.slice(0, index);
																		setParseList([prevParseList => parseList]);
																	}
																});
																parseList.splice(index, 1);
																setParseList(prevParseList => ([...parseList]));
																bridge.send("VKWebAppTapticImpactOccurred", {"style": "medium"}).catch(() => {});
																e.stopPropagation();
															}}
														/>
													}
												>{item.account}</SimpleCell>
		                  ))}
		                </List>
		              </Group>
									<Group header={<Header mode="secondary">Данные</Header>}>
										<Search value={search} onChange={onSearch} after={null} />
										{parseList.map((item) => (
											<SimpleCell
												before={<Avatar mode="image" src={item.data.image} />}
												description={item.data.hashtag}
											>{item.data.text}</SimpleCell>
										))}
									</Group>
								</>
							)}
					</Panel>
				</View>
			</ConfigProvider>
		</ErrorBoundary>
	);
}

export default App;